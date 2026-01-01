from dataclasses import dataclass
from enum import Enum, auto

class RawEntryType(Enum):
    TRANSACTION = auto()
    BALANCE = auto()
    UNKNOW = auto()

@dataclass
class RawEntry:
    date : str
    amount : str
    comment : str
    account_idx : int
    type : RawEntryType
