from typing import List, Dict
from TimeInterval import TimeInterval, TimeIntervalVariants
from Types import *
import datetime
import logging

class EntryFilter:
    
    @staticmethod
    def formated_date(date : datetime.date) -> str:
        return f"{date.year}-{date.month}"

    @staticmethod
    def external_transactions(entries : List[InterpretedEntry]):
        return [entry for entry in entries 
                      if     entry.type == InterpretedType.TRANSACTION_EXTERNAL 
                         and Tag.ACCOUNT_SAVINGS not in entry.tags]

    @staticmethod
    def undefined_transactions(entries : List[InterpretedEntry]):
        return [entry for entry in entries 
                      if     entry.raw.type == StatementType.TRANSACTION 
                         and Tag.UNDEFINED in entry.tags]
    
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
    def tag(entries : List[InterpretedEntry], tag : Tag):
        return [entry for entry in entries if tag in entry.tags]

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
    def balance_per_tag_of_interval(entries : List[InterpretedEntry], interval : TimeInterval) -> Dict[Tag, float]:
        balance_per_tag : Dict[Tag, float] = {}
        for entry in entries:
            curr_interval = TimeInterval.create_from_date(interval.get_variant(), entry.date)
            curr_tag = None
            if interval == curr_interval:
                if len(entry.tags) == 1:
                    curr_tag = entry.tags[0]
                elif entry.amount == 0.0:
                    continue
                elif len(entry.tags) > 1:
                    logging.warning(f"Entry has more than one tag. Only using first one. {entry}")
                    curr_tag = entry.tags[0]
                if curr_tag in balance_per_tag:
                    balance_per_tag[curr_tag] += entry.amount
                else:
                    balance_per_tag[curr_tag] = entry.amount
        return balance_per_tag