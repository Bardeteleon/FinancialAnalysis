

import datetime
from user_interface.logger import logger
import re
from typing import Dict, List, Optional
from data_types.Config import Account
from statement.EntryFilter import EntryFilter
from statement.EntryInsights import EntryInsights
from data_types.TimeInterval import TimeInterval, TimeIntervalVariants, YearInterval
from data_types.Types import InterpretedEntry
from data_types.TagGroup import TagGroup


class EntryMapping:
    
    @staticmethod
    def account_index_to_id(entries : List[InterpretedEntry]) -> Dict[int, str]:
        return {entry.raw.account_idx : entry.account_id for entry in entries if entry.raw is not None}

    @staticmethod
    def balance_per_interval(entries : List[InterpretedEntry], interval_variant : TimeIntervalVariants) -> Dict[TimeInterval, float]:
        balance_per_time_interval : Dict[TimeInterval, float] = {}
        for entry in entries:
            interval : TimeInterval = TimeInterval.create_from_date(interval_variant, entry.date)
            if interval in balance_per_time_interval:
                balance_per_time_interval[interval] += entry.amount
            else:
                balance_per_time_interval[interval] = entry.amount
        balance_per_time_interval = dict(sorted(balance_per_time_interval.items(), 
                                                key=lambda x: x[0], 
                                                reverse=False))
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
            account_id = account.transaction_iban if account.is_virtual() else account_index_to_id[account_idx]
            result[account.name] = EntryMapping.__sum_amounts(
                                        EntryFilter.transactions(all_entries, main_id=account_id),
                                        until_interval)
            initial_balance = EntryInsights.initial_balance(all_entries, account_id)
            logger.debug(f"Account {account.name} has initial balance {initial_balance} and transaction sum {result[account.name]}")
            result[account.name] += initial_balance
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