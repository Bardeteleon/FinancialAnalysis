from dataclasses import dataclass
from enum import Enum, auto

class RawEntryType(Enum):
    TRANSACTION = auto()
    BALANCE = auto()
    UNKNOW = auto()

@dataclass
class RawEntry:
    date : str = ""
    amount : str = ""
    comment : str = ""
    account_idx : int = 0
    type : RawEntryType = RawEntryType.UNKNOW

    def is_transaction(self) -> bool:
        return self.type == RawEntryType.TRANSACTION

    def is_balance(self) -> bool:
        return self.type == RawEntryType.BALANCE
