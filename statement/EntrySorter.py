from data_types.Types import *
from typing import List


class EntrySorter:

    @staticmethod
    def by_amount(entries : List[InterpretedEntry], reverse=True):
        return sorted(entries, key=lambda entry: entry.amount, reverse=reverse)
    
    @staticmethod
    def by_date(entries : List[InterpretedEntry], reverse=True):
        return sorted(entries, key=lambda entry: entry.date, reverse=reverse)