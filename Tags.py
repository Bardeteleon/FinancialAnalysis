
# from __future__ import annotations Does not work together with dataconf! ...
import datetime
import dataconf
from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional

class Tag(Enum):
    UNDEFINED = auto()
    ACTIVITIES = auto()
    CAR = auto()
    CASH = auto()
    CREDIT_CARD = auto()
    DOCTOR = auto()
    DONATION = auto()
    HARDWARE_STORE = auto()
    HOLIDAY = auto()
    HOLIDAY_MADEIRA = auto()
    INSURANCE = auto()
    INTERNET = auto()
    MEDIA = auto()
    OFFLINE_SHOPPING = auto()
    ONLINE_SHOPPING = auto()
    OTHER_INCOME = auto()
    PETROL = auto()
    PHARMACY = auto()
    PUBLIC_TRANSPORT = auto()
    RENT = auto()
    RESTAURANT = auto()
    SALARY = auto()
    SAVINGS = auto()
    SUPERMARKET = auto()
    TRAVEL = auto()
    BANK_FEES = auto()

@dataclass
class TagPattern:
    pattern : str
    tag : Tag
    date_from : Optional[str]
    date_to : Optional[str]

@dataclass
class Tags:
    tags : List[TagPattern]

def load_tags(file_path : str) -> Tags:
    return dataconf.load(file_path, Tags)
