from datetime import date, timedelta
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Set
from data_types.Config import Config
from data_types.InterpretedEntry import CardType, InterpretedEntry, InterpretedEntryType
from data_types.RawEntry import RawEntryType
from statement.EntryMapping import EntryMapping
from user_interface.logger import logger
import re
import numpy

class RatingReason(Enum):
    MATCH_REFERENCED_BY_ENTRY_WITH_OWNER = "match_referenced_by_entry_with_owner"
    ENTRY_REFERENCED_BY_MATCH_WITH_OWNER = "entry_referenced_by_match_with_owner"
    MATCH_REFERENCED_BY_ENTRY_WITH_ID = "match_referenced_by_entry_with_id"
    ENTRY_REFERENCED_BY_MATCH_WITH_ID = "entry_referenced_by_match_with_id"

@dataclass
class RatedEntry:
    entry : InterpretedEntry
    points : float
    reasons : List[RatingReason]

class RatedEntryBuilder:
    def __init__(self, entry : InterpretedEntry):
        self.__entry = entry
        self.__points = 0.0
        self.__reasons = []
    
    def add_rating(self, reason : RatingReason):
        self.__points += self.__get_points_for_reason(reason)
        self.__reasons.append(reason)

    def build(self):
        return RatedEntry(self.__entry, self.__points, self.__reasons)

    def __get_points_for_reason(self, reason : RatingReason):
        if reason == RatingReason.MATCH_REFERENCED_BY_ENTRY_WITH_OWNER:
            return 1.0
        elif reason == RatingReason.ENTRY_REFERENCED_BY_MATCH_WITH_OWNER:
            return 1.0
        elif reason == RatingReason.MATCH_REFERENCED_BY_ENTRY_WITH_ID:
            return 2.0
        elif reason == RatingReason.ENTRY_REFERENCED_BY_MATCH_WITH_ID:
            return 2.0
        else:
            return 0.0

@dataclass
class MaybeMatch:
    entry : InterpretedEntry
    matches : List[RatedEntry]

""" Extracts fields for interpreted entries that need consideration of the whole statement.
"""
class InterpretedStatementExtractor:
    def __init__(self, entries : List[InterpretedEntry], config : Config):
        self.__entries : List[InterpretedEntry] = entries
        self.__config : Config = config
        self.__entries_by_year_week : Dict[int, Dict[int, List[InterpretedEntry]]] = EntryMapping.entries_per_year_and_week(entries)

    def run(self):
        self.__extract_type()

    def __extract_type(self):

        maybe_matches : Dict[int, MaybeMatch] = {} # for internal transactions

        for entry in self.__entries:

            if entry.type == InterpretedEntryType.BALANCE:
                continue
            elif entry.raw and entry.raw.type == RawEntryType.BALANCE:
                entry.type = InterpretedEntryType.BALANCE
            elif entry.raw and entry.raw.type == RawEntryType.UNKNOW:
                entry.type = InterpretedEntryType.UNKNOWN
            elif entry.card_type == CardType.CREDIT and entry.amount < 0.0:
                entry.type = InterpretedEntryType.TRANSACTION_EXTERNAL
            else:
                nearby_entries = self.__get_entries_near_date(entry.date, plus_minus_weeks=1) # manual sync with max_days_diff, consider possible non busy days (weekends)
                matching_entries = self.__find_matching_internal_transactions(entry, nearby_entries, max_days_diff=5)
                matching_rated_entries : List[RatedEntry] = []
                for matching_entry in matching_entries:
                    matching_rated_entries.append(self.__evaluate_rated_entry(entry, matching_entry))
                matching_rated_entries.sort(key=lambda e: e.points, reverse=True)
                maybe_matches[id(entry)] = MaybeMatch(entry, matching_rated_entries)

        processed_entries = set()
        minimum_required_points = 2.0

        # Resolve collected maybe matches with their points.
        # 
        # Goal: Match as many transactions which have a given minimum amount of points.
        # 
        # Strategy: 
        #   Follow the match with highest points. 
        #   Does the matching entry has as well a match with highest points back to the original entry? 
        #   If yes, 
        #       fine, its an internal transaction match.
        #   If no, 
        #       follow the match with highest points and resolve it eventually.
        #       Continue and check the next match (with highest points) if it points back to the original entry.
        # The strategy proritizes matches with highest points. Thus an entry with low points which would match to an 
        # entry with high points might not be realized because the entry with high points is already matched to another 
        # entry with high points. To overcome this an optimization problem must be solved. Or (workaround) add more 
        # matching information in the shape of points to increase the gap between low and hight points.
        def resolve(entry : InterpretedEntry, 
                    maybe_match : MaybeMatch, 
                    processed_entries : Set[int] = processed_entries, 
                    maybe_matches : Dict[int, MaybeMatch] = maybe_matches,
                    minimum_required_points : float = minimum_required_points):
            entry_id = id(entry)

            if entry_id in processed_entries:
                return

            for backwards_match in maybe_match.matches:
                backwards_matched_entry_id = id(backwards_match.entry)
                if backwards_matched_entry_id in processed_entries:
                    continue
                if backwards_match.points < minimum_required_points:
                    return # matches sorted by points so no continue needed and already too low points for a match
                if backwards_matched_entry_id == entry_id:
                    entry.type = InterpretedEntryType.TRANSACTION_INTERNAL
                    entry.internal_transaction_match = maybe_match.entry
                    processed_entries.add(entry_id)
                    maybe_match.entry.type = InterpretedEntryType.TRANSACTION_INTERNAL
                    maybe_match.entry.internal_transaction_match = entry
                    processed_entries.add(id(maybe_match.entry))
                    return
                else:
                    resolve(maybe_match.entry, maybe_matches[backwards_matched_entry_id])
                    if id(maybe_match.entry) in processed_entries or entry_id in processed_entries:
                        return
                    else:
                        continue

        for entry_id, maybe_match in maybe_matches.items():
            if entry_id in processed_entries:
                continue
            for match in maybe_match.matches:
                if id(match.entry) in processed_entries:
                    continue
                if match.points < minimum_required_points:
                    break # matches sorted by points so no continue needed and already too low points for a match
                resolve(maybe_match.entry, maybe_matches[id(match.entry)])
                
            if entry_id not in processed_entries:
                maybe_match.entry.type = InterpretedEntryType.TRANSACTION_EXTERNAL
                processed_entries.add(entry_id)


    def __evaluate_rated_entry(self, entry: InterpretedEntry, match: InterpretedEntry) -> 'RatedEntry':
        rated_entry_builder = RatedEntryBuilder(match)

        # Handle case that entries are virtual and have not comment but are already set to internal
        entry_comment = entry.raw.comment if not entry.is_virtual() else match.account_id if entry.is_internal() else ""
        match_comment = match.raw.comment if not match.is_virtual() else entry.account_id if match.is_internal() else ""

        entry_references_match_by_id = match.account_id in entry_comment
        match_references_entry_by_id = entry.account_id in match_comment

        entry_references_match_by_owner = self.__comment_contains_account_owners(entry_comment, match.account_id)
        match_references_entry_by_owner = self.__comment_contains_account_owners(match_comment, entry.account_id)

        if entry_references_match_by_id:
            rated_entry_builder.add_rating(RatingReason.MATCH_REFERENCED_BY_ENTRY_WITH_ID)
        elif entry_references_match_by_owner:
            rated_entry_builder.add_rating(RatingReason.MATCH_REFERENCED_BY_ENTRY_WITH_OWNER)

        if match_references_entry_by_id:
            rated_entry_builder.add_rating(RatingReason.ENTRY_REFERENCED_BY_MATCH_WITH_ID)
        elif match_references_entry_by_owner:
            rated_entry_builder.add_rating(RatingReason.ENTRY_REFERENCED_BY_MATCH_WITH_OWNER)

        return rated_entry_builder.build()

    def __comment_contains_account_owners(self, comment: str, account_id: str) -> bool:
        for reference in self.__get_account_owners(account_id):
            if reference in comment:
                return True
        return False

    def __find_matching_internal_transactions(self,
                                             entry: InterpretedEntry,
                                             all_entries: List[InterpretedEntry],
                                             processed_entries: Set[int] = set(),
                                             max_days_diff: int = 5,
                                             amount_tolerance: float = 0.1) -> List[InterpretedEntry]:
        if entry.raw and entry.raw.type != RawEntryType.TRANSACTION:
            return None

        target_amount = -entry.amount

        candidates = []

        for candidate in all_entries:
            if id(candidate) in processed_entries:
                continue

            if candidate.is_balance():
                continue

            if candidate.account_id == entry.account_id:
                continue

            if candidate.raw and candidate.raw.type != RawEntryType.TRANSACTION:
                continue

            day_diff = self.__calculate_day_difference(entry.date, candidate.date)
            if day_diff > max_days_diff:
                continue

            amount_diff = abs(candidate.amount - target_amount)
            if amount_diff > amount_tolerance:
                continue

            candidates.append(candidate)

        return candidates
    
    def __get_account_owners(self, account_id: str) -> List[str]:
        references = []
        for account in self.__config.internal_accounts:
            if account.get_id() == account_id:
                if account.owner:
                    references.extend(account.owner)
                break
        return references

    def __get_entries_near_date(self, target_date: date, plus_minus_weeks: int = 1) -> List[InterpretedEntry]:
        nearby_entries = []

        for week_offset in range(-plus_minus_weeks, plus_minus_weeks + 1):
            check_date = target_date + timedelta(weeks=week_offset)
            check_year = check_date.year
            check_week = check_date.isocalendar().week

            if check_year in self.__entries_by_year_week and check_week in self.__entries_by_year_week[check_year]:
                nearby_entries.extend(self.__entries_by_year_week[check_year][check_week])

        return nearby_entries

    @staticmethod
    def __calculate_day_difference(date1: date, date2: date) -> int:
        return abs(numpy.busday_count(date1, date2))
