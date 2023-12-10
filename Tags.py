
# from __future__ import annotations Does not work together with dataconf! ...
import dataconf
from enum import Enum, auto
from dataclasses import dataclass
from typing import List

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
class TagPattern:
    pattern : str
    tag : Tag

@dataclass
class Tags:
    tags : List[TagPattern]

def load_tags(file_path : str) -> Tags:
    return dataconf.load(file_path, Tags)
