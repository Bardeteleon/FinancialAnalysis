from dataclasses import dataclass
from enum import Enum, auto
from datetime import date
from typing import List

class StatementType(Enum):
    TRANSACTION = auto()
    BALANCE = auto() 
    UNKNOW = auto()

class Tag(Enum):
    UNDEFINED = auto()
    SALARY = auto()
    OTHER_INCOME = auto()
    RENT = auto()
    SUPERMARKET = auto()
    SAVINGS = auto()
    ONLINE_SHOPPING = auto()
    PETROL = auto()
    MEDIA = auto()
    ACCOUNT_SAVINGS = auto()
    ACCOUNT_SPENDINGS = auto()
    INTERNET = auto()
    HARDWARE_STORE = auto()
    CREDIT_CARD = auto()
    INSURANCE = auto()
    PHARMACY = auto()
    OFFLINE_SHOPPING = auto()
    RESTAURANT = auto()
    ACTIVITIES = auto()
    TRAVEL = auto()
    DONATION = auto()
    CASH = auto()

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

@dataclass
class TagPattern:
    pattern : str
    tag : Tag
