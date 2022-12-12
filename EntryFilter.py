from typing import List, Dict
from Types import *
import datetime

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
    def balance_per_month(entries : List[InterpretedEntry]) -> Dict[str, float]:
        balance_per_month : Dict[str, float] = {}
        for entry in entries:
            month : str = EntryFilter.formated_date(entry.date)
            if month in balance_per_month:
                balance_per_month[month] += entry.amount
            else:
                balance_per_month[month] = entry.amount
        return balance_per_month