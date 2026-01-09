from datetime import date, timedelta
from typing import Dict, List, Optional, Set
from data_types.Config import Config
from data_types.InterpretedEntry import CardType, InterpretedEntry, InterpretedEntryType
from data_types.RawEntry import RawEntryType
from statement.EntryMapping import EntryMapping
from user_interface.logger import logger
import re
import numpy

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
        processed_entries = set()

        for entry in self.__entries:
            if id(entry) in processed_entries:
                continue

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
                matching_entry = self.__find_matching_internal_transaction(entry, nearby_entries, processed_entries, max_days_diff=5)
                if matching_entry and self.__is_internal_transaction_pair(entry, matching_entry):
                    entry.type = InterpretedEntryType.TRANSACTION_INTERNAL
                    matching_entry.type = InterpretedEntryType.TRANSACTION_INTERNAL
                    processed_entries.add(id(matching_entry))
                else:
                    entry.type = InterpretedEntryType.TRANSACTION_EXTERNAL

            processed_entries.add(id(entry))

    def __is_internal_transaction_pair(self, entry1: InterpretedEntry, entry2: InterpretedEntry) -> bool:

        # Handle case that entries are virtual and have not comment but are already set to internal
        # TODO maybe not needed with only one way reference
        comment1 = entry1.raw.comment if not entry1.is_virtual() else entry2.account_id if entry1.is_internal() else ""
        comment2 = entry2.raw.comment if not entry2.is_virtual() else entry1.account_id if entry2.is_internal() else ""

        entry1_references_entry2_by_id = entry2.account_id in comment1
        entry2_references_entry1_by_id = entry1.account_id in comment2

        entry1_references_entry2_by_owner = self.__comment_contains_account_owners(comment1, entry2.account_id)
        entry2_references_entry1_by_owner = self.__comment_contains_account_owners(comment2, entry1.account_id)

        is_internal = (entry1_references_entry2_by_id or entry2_references_entry1_by_id) or \
                      (entry1_references_entry2_by_owner and entry2_references_entry1_by_owner)
        return is_internal

    def __comment_contains_account_owners(self, comment: str, account_id: str) -> bool:
        for reference in self.__get_account_owners(account_id):
            if reference in comment:
                return True
        return False

    def __find_matching_internal_transaction(self,
                                             entry: InterpretedEntry,
                                             all_entries: List[InterpretedEntry],
                                             processed_entries: Set[int],
                                             max_days_diff: int = 5,
                                             amount_tolerance: float = 0.1) -> Optional[InterpretedEntry]:
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

            date_diff = self.__calculate_date_difference(entry.date, candidate.date)
            if date_diff > max_days_diff:
                continue

            amount_diff = abs(candidate.amount - target_amount)
            if amount_diff > amount_tolerance:
                continue

            candidates.append(candidate)

        candidates.sort(key=lambda candidate: self.__calculate_date_difference(entry.date, candidate.date))

        if len(candidates) > 0:
            return candidates[0]
        else:
            return None

    def __get_account_references(self, account_id: str) -> List[str]:
        references = []
        for account in self.__config.internal_accounts:
            if account.get_id() == account_id:
                references.append(account.get_id())
                if account.owner:
                    references.extend(account.owner)
                break
        return references
    
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
    def __calculate_date_difference(date1: date, date2: date) -> int:
        return abs(numpy.busday_count(date1, date2))
