from Types import *
from typing import List


class EntrySorter:

    @staticmethod
    def by_amount(entries : List[InterpretedEntry], reverse=True):
        return sorted(entries, key=lambda entry: entry.amount, reverse=reverse)