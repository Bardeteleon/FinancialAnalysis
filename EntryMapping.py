

import datetime
import logging
from typing import Dict, List, Optional
from Config import Account
from EntryFilter import EntryFilter
from EntryInsights import EntryInsights
from TimeInterval import TimeInterval, TimeIntervalVariants, YearInterval
from Types import InterpretedEntry
from tagging.TagGroup import TagGroup


class EntryMapping:
    
    @staticmethod
    def account_index_to_id(entries : List[InterpretedEntry]) -> Dict[int, str]:
        return {entry.raw.account_idx : entry.account_id for entry in entries if entry.raw is not None}

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
        account_index_to_id = EntryMapping.account_index_to_id(all_entries)
        for account_idx, account in enumerate(all_accounts):
            if account_idx in account_index_to_id.keys():
                result[account.name] = EntryMapping.__sum_amounts(
                                            EntryFilter.transactions(all_entries, main_id=account_index_to_id[account_idx]),
                                            until_interval)
                initial_balance = EntryInsights.initial_balance(all_entries, account_index_to_id[account_idx])
                logging.debug(f"Account {account.name} has initial balance {initial_balance} and transaction sum {result[account.name]}")
                result[account.name] += initial_balance
            else:
                result[account.name] = EntryMapping.__sum_amounts(
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