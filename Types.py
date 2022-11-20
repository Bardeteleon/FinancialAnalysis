from dataclasses import dataclass
from enum import Enum, auto
from datetime import date
from typing import List

class StatementType(Enum):
    TRANSACTION = auto()
    BALANCE = auto() 
    UNKNOW = auto()

class Tag(Enum):
    SALARY = auto()
    RENT = auto()
    SUPERMARKET = auto()

@dataclass
class RawEntry:
    date : str
    amount : str
    comment : str
    type : StatementType

@dataclass
class InterpretedEntry:
    date : date
    amount : float
    tags : List[Tag]
    raw : RawEntry