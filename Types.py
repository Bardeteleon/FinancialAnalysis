from dataclasses import dataclass
from enum import Enum, auto
from datetime import date
from typing import List
from Tags import Tag

class StatementType(Enum):
    TRANSACTION = auto()
    BALANCE = auto() 
    UNKNOW = auto()

class InterpretedType(Enum):
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
    identification : str
    type : StatementType

@dataclass
class InterpretedEntry:
    date : date = None
    amount : float = 0.0
    tags : List[Tag] = None
    card_type : CardType = None
    account_id : str = ""
    type : InterpretedType = InterpretedType.UNKNOWN
    raw : RawEntry = None
