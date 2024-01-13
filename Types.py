from dataclasses import dataclass
from enum import Enum, auto
from datetime import date
from typing import List
from tagging.Tag import Tag

class RawEntryType(Enum):
    TRANSACTION = auto()
    BALANCE = auto() 
    UNKNOW = auto()

class InterpretedEntryType(Enum):
    TRANSACTION_INTERNAL = auto()
    TRANSACTION_EXTERNAL = auto()
    BALANCE = auto()
    UNKNOWN = auto()

class CardType(Enum):
    CREDIT = auto()
    GIRO = auto()

@dataclass
class RawEntry:
    date : str
    amount : str
    comment : str
    account_idx : int
    type : RawEntryType

@dataclass
class InterpretedEntry:
    date : date = None
    amount : float = 0.0
    tags : List[Tag] = None
    card_type : CardType = None
    account_id : str = ""
    type : InterpretedEntryType = InterpretedEntryType.UNKNOWN
    raw : RawEntry = None

    def is_untagged(self) -> bool:
        return self.tags == None or len(self.tags) == 0
