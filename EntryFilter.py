from typing import List
from Types import *


class EntryFilter:

    @staticmethod
    def external_transactions(entries : List[InterpretedEntry]):
        return [entry for entry in entries 
                      if     entry.raw.type == StatementType.TRANSACTION 
                         and Tag.ACCOUNT_SAVINGS not in entry.tags]

    def tag_undefined(entries : List[InterpretedEntry]):
        return [entry for entry in entries if Tag.UNDEFINED in entry.tags]