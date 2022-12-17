from typing import List, Dict
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
                      if     entry.raw.type == StatementType.TRANSACTION 
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
    def balance_per_month(entries : List[InterpretedEntry]) -> Dict[str, float]:
        balance_per_month : Dict[str, float] = {}
        for entry in entries:
            month : str = EntryFilter.formated_date(entry.date)
            if month in balance_per_month:
                balance_per_month[month] += entry.amount
            else:
                balance_per_month[month] = entry.amount
        return balance_per_month

    @staticmethod
    def balance_per_tag_of_month(entries : List[InterpretedEntry], month : str) -> Dict[Tag, float]:
        balance_per_tag : Dict[Tag, float] = {}
        for entry in entries:
            curr_month = EntryFilter.formated_date(entry.date)
            curr_tag = None
            if month == curr_month:
                if len(entry.tags) == 1:
                    curr_tag = entry.tags[0]
                elif len(entry.tags) > 1:
                    logging.warning(f"Entry has more than one tag. Only using first one. {entry}")
                    curr_tag = entry.tags[0]
                if curr_tag in balance_per_tag:
                    balance_per_tag[curr_tag] += entry.amount
                else:
                    balance_per_tag[curr_tag] = entry.amount
        return balance_per_tag