from copy import deepcopy
from typing import Callable, List, Dict, Optional, Set, Tuple
from Config import Account, CustomBalance
from TimeInterval import TimeInterval, TimeIntervalVariants, YearInterval
from Types import *
from tagging.Tag import Tag, UndefinedTag
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
    def transactions(entries : List[InterpretedEntry], main_id : Optional[str] = None, other_id : Optional[str] = None):
        return [entry for entry in entries if entry.raw and
                                              entry.raw.type == RawEntryType.TRANSACTION and 
                                              (main_id == None or entry.account_id == main_id) and 
                                              (other_id == None or re.search(other_id, entry.raw.comment))]

    @staticmethod
    def custom_balance(balance_type_to_data : Dict[str, Callable], custom_balance : CustomBalance):

        def get_matches_in_a_list(input, list) -> List[str]:
            result = []
            for item in list:
                if re.search(re.escape(input), item):
                    result.append(item)
            return result

        result = []

        name_results = get_matches_in_a_list(custom_balance.name, custom_balance.plus + custom_balance.minus)
        if len(name_results) > 0:
            logging.error(f"Custom balance '{custom_balance.name}' contains itself in its definition (plus/minus).")
            return result

        for plus in custom_balance.plus:
            plus_results = get_matches_in_a_list(plus, balance_type_to_data.keys())
            if len(plus_results) == 0:
                logging.info(f"No match for custom balance {custom_balance.name} with plus {plus}")
            for plus_result in plus_results:
                result = result + balance_type_to_data[plus_result]()
        for minus in custom_balance.minus:
            minus_results = get_matches_in_a_list(minus, balance_type_to_data.keys())
            if len(minus_results) == 0:
                logging.info(f"No match for custom balance {custom_balance.name} with minus {minus}")
            for minus_result in minus_results:
                result = result + EntryFilter.reverse_sign_of_amounts(balance_type_to_data[minus_result]())
        return result

    @staticmethod
    def reverse_sign_of_amounts(entries : List[InterpretedEntry]) -> List[InterpretedEntry]:
        result = deepcopy(entries)
        for entry in result:
            entry.amount = -1 * entry.amount
        return result

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
    
    @staticmethod
    def balance_per_account_until_interval(all_entries : List[InterpretedEntry], until_interval : TimeInterval, all_accounts : List[Account]) -> Dict[str, float]:
        result : Dict[str, float] = {}
        account_index_to_id = EntryFilter.account_index_to_id(all_entries)
        for account_idx, account in enumerate(all_accounts):
            if account_idx in account_index_to_id.keys():
                result[account.name] = EntryFilter.__sum_amounts(
                                            EntryFilter.transactions(all_entries, main_id=account_index_to_id[account_idx]),
                                            until_interval)
            else:
                result[account.name] = EntryFilter.__sum_amounts(
                                            EntryFilter.reverse_sign_of_amounts(
                                            EntryFilter.transactions(all_entries, other_id=account.transaction_iban)),
                                            until_interval)
        return result
    
    @staticmethod
    def __sum_amounts(entries : List[InterpretedEntry], until_interval : Optional[TimeInterval] = None) -> float:
        result : float = 0.0
        if until_interval is None:
            until_interval = YearInterval(datetime.date(datetime.MAXYEAR, 1, 1))
        for entry in entries:
            if TimeInterval.create_from_date(until_interval.get_variant(), entry.date) <= until_interval:
                result += entry.amount 
        return result