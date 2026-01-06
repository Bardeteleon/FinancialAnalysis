
import datetime
from data_types.Config import Account
from data_types.TagGroup import TagGroup
from data_types.TimeInterval import TimeInterval, TimeIntervalVariants, YearInterval
from statement.EntryValidator import EntryValidator
from user_interface.logger import logger
from typing import Dict, List, Optional
from statement.EntryFilter import EntryFilter
from data_types.InterpretedEntry import InterpretedEntry, InterpretedEntryType
from data_types.Tag import UndefinedTag
from collections import Counter
from dataclasses import dataclass

class EntryInsights:

    @staticmethod
    def initial_balance(entries : List[InterpretedEntry], account_id : str) -> float:
        result : float = 0.0
        account_entries = EntryFilter.account(entries, account_id)
        if not EntryValidator.have_ascending_date_order(account_entries):
            logger.debug(f"Account entries of {account_id} do not have ascending date order, initial balance not derived")
            return result
        first_index_with_balance : Optional[int] = EntryInsights.__get_first_index_with_balance(account_entries)
        if first_index_with_balance is not None:
            result = sum([ -1.0*entry.amount for entry in account_entries[:first_index_with_balance] if entry.is_transaction()])
            result += account_entries[first_index_with_balance].amount
        else:
            logger.debug(f"No entry with type balance found for accound id {account_id}")
        return result
    
    @staticmethod
    def __get_first_index_with_balance(entries : List[InterpretedEntry]) -> Optional[int]:
        for i, entry in enumerate(entries):
            if entry.type == InterpretedEntryType.BALANCE:
                return i
        return None

    @staticmethod
    def initial_balance_if_entries_with_unique_account_unless_zero(entries : List[InterpretedEntry]) -> float:
        result : float = 0.0
        accounts = list(EntryFilter.unique_accounts(entries))
        if len(accounts) == 1: 
            account_id = accounts[0]
            result = EntryInsights.initial_balance(entries, account_id)
            logger.debug(f"Found only entries of account {account_id} with initial balance {result}")
        return result


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
        for account in all_accounts:
            account_id = account.get_id()
            result[account.name] = EntryInsights.__sum_amounts(
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

    @dataclass
    class Statistics:
        total : int
        external : int
        internal : int
        balances : int
        tagged : int

    @staticmethod
    def statistics(entries : List[InterpretedEntry]) -> Statistics:
        counts = Counter()
        for entry in entries:
            counts[entry.type] += 1
            counts["tagged"] += 1 if entry.is_tagged() and UndefinedTag not in entry.tags else 0

        return EntryInsights.Statistics(total=len(entries), 
                                        external=counts[InterpretedEntryType.TRANSACTION_EXTERNAL], 
                                        internal=counts[InterpretedEntryType.TRANSACTION_INTERNAL], 
                                        balances=counts[InterpretedEntryType.BALANCE], 
                                        tagged=counts["tagged"])
        