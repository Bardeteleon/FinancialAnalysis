from typing import List, Dict, Optional, Set, Tuple
from TimeInterval import TimeInterval, TimeIntervalVariants
from Types import *
from tagging.NewTag import Tag, UndefinedTag
import datetime
import logging
import re

from tagging.TagGroup import TagGroup

class EntryFilter:
    
    @staticmethod
    def formated_date(date : datetime.date) -> str:
        return f"{date.year}-{date.month}"

    @staticmethod
    def external_transactions(entries : List[InterpretedEntry]):
        return [entry for entry in entries 
                      if entry.type == InterpretedEntryType.TRANSACTION_EXTERNAL]

    @staticmethod
    def undefined_transactions(entries : List[InterpretedEntry]):
        return [entry for entry in entries 
                      if     entry.raw.type == RawEntryType.TRANSACTION 
                         and (entry.is_untagged() or UndefinedTag in entry.tags)]
    
    @staticmethod
    def positive_amount(entries : List[InterpretedEntry]):
        return [entry for entry in entries if entry.amount >= 0.0]
    
    @staticmethod
    def negative_amount(entries : List[InterpretedEntry]):
        return [entry for entry in entries if entry.amount < 0.0]

    @staticmethod
    def no_zero_amount(entries : List[InterpretedEntry]):
        return [entry for entry in entries if entry.amount != 0.0]

    @staticmethod
    def tag(entries : List[InterpretedEntry], given_tag : Tag):
        return [entry for entry in entries for tag in entry.tags if given_tag.contains(tag)]

    @staticmethod
    def transactions(entries : List[InterpretedEntry], main_id : str, other_id : str):
        return [entry for entry in entries if entry.raw and
                                              entry.raw.type == RawEntryType.TRANSACTION and 
                                              (main_id == None or entry.account_id == main_id) and 
                                              (other_id == None or re.search(other_id, entry.raw.comment))]

    @staticmethod
    def account_index_to_id(entries : List[InterpretedEntry]) -> Set[Dict[int, str]]:
        return {entry.raw.account_idx : entry.account_id for entry in entries}

    @staticmethod
    def balance_per_interval(entries : List[InterpretedEntry], interval_variant : TimeIntervalVariants) -> Dict[str, float]:
        balance_per_time_interval : Dict[str, float] = {}
        for entry in entries:
            interval_str : str = TimeInterval.create_from_date(interval_variant, entry.date).to_string()
            if interval_str in balance_per_time_interval:
                balance_per_time_interval[interval_str] += entry.amount
            else:
                balance_per_time_interval[interval_str] = entry.amount
        return balance_per_time_interval

    @staticmethod
    def balance_per_tag_of_interval(entries : List[InterpretedEntry], requested_interval : TimeInterval) -> Dict[TagGroup, float]:
        balance_per_tag : Dict[TagGroup, float] = {}
        for entry in entries:
            if entry.amount == 0.0:
                    continue
            curr_interval = TimeInterval.create_from_date(requested_interval.get_variant(), entry.date)
            curr_tag = TagGroup()
            if requested_interval == curr_interval:
                for tag in entry.tags:
                    curr_tag.add(tag)
                if curr_tag in balance_per_tag:
                    balance_per_tag[curr_tag] += entry.amount
                else:
                    balance_per_tag[curr_tag] = entry.amount
        return balance_per_tag