from dataclasses import dataclass
from enum import Enum, auto
from datetime import date
from typing import List

class StatementType(Enum):
    TRANSACTION = auto()
    BALANCE = auto() 
    UNKNOW = auto()

class CardType(Enum):
    CREDIT = auto()
    GIRO = auto()

class Tag(Enum):
    UNDEFINED = auto()
    ACCOUNT_EXPENSES = auto()
    ACCOUNT_SAVINGS = auto()
    ACCOUNT_RISK = auto()
    ACTIVITIES = auto()
    CAR = auto()
    CASH = auto()
    CREDIT_CARD = auto()
    DOCTOR = auto()
    DONATION = auto()
    HARDWARE_STORE = auto()
    HOLIDAY = auto()
    INSURANCE = auto()
    INTERNET = auto()
    MEDIA = auto()
    OFFLINE_SHOPPING = auto()
    ONLINE_SHOPPING = auto()
    OTHER_INCOME = auto()
    PETROL = auto()
    PHARMACY = auto()
    RENT = auto()
    RESTAURANT = auto()
    SALARY = auto()
    SAVINGS = auto()
    SUPERMARKET = auto()
    TRAVEL = auto()

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
    raw : RawEntry = None

@dataclass
class TagPattern:
    pattern : str
    tag : Tag
