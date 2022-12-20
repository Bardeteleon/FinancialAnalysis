from __future__ import annotations
from enum import Enum, auto
from typing import Optional

import re
import datetime

class TimeIntervalVariants(Enum):
    MONTH = auto()
    QUARTER = auto()
    HALF_YEAR = auto()
    YEAR = auto()

class TimeInterval:

    def __eq__(self, interval : object) -> bool:
        return False

    def to_string(self) -> str:
        return ""

    @staticmethod
    def create_from_string(interval_variant : TimeIntervalVariants, string : str) -> Optional[TimeInterval]:
        if interval_variant == TimeIntervalVariants.MONTH:
            return MonthInterval.from_string(string)
        elif interval_variant == TimeIntervalVariants.QUARTER:
            return QuarterInterval.from_string(string)
        elif interval_variant == TimeIntervalVariants.HALF_YEAR:
            return HalfYearInterval.from_string(string)
        elif interval_variant == TimeIntervalVariants.YEAR:
            return YearInterval.from_string(string)
        else:
            return None

    def get_variant(self) -> TimeIntervalVariants:
        return TimeIntervalVariants.MONTH

    @staticmethod
    def create_from_date(interval_variant : TimeIntervalVariants, date : datetime.date) -> Optional[TimeInterval]:
        if interval_variant == TimeIntervalVariants.MONTH:
            return MonthInterval(date)
        elif interval_variant == TimeIntervalVariants.QUARTER:
            return QuarterInterval(date)
        elif interval_variant == TimeIntervalVariants.HALF_YEAR:
            return HalfYearInterval(date)
        elif interval_variant == TimeIntervalVariants.YEAR:
            return YearInterval(date)
        else:
            return None


class MonthInterval(TimeInterval):

    def __init__(self, date : datetime.date):
        self.__year : int = date.year
        self.__month : int = date.month

    def __eq__(self, interval : object) -> bool:
        if isinstance(interval, MonthInterval):
            return self.__year == interval.__year and self.__month == interval.__month
        else:
            return False

    def to_string(self) -> str:
        return f"{self.__year}-{self.__month}"
    
    @staticmethod
    def from_string(string : str) -> Optional[MonthInterval]:
        match = re.search("^(\d{4})-(\d{1,2})$", string)
        if match:
            return MonthInterval(datetime.date(year=int(match.group(1)), month=int(match.group(2)), day=1))
        else:
            return None

    def get_variant(self) -> TimeIntervalVariants:
        return TimeIntervalVariants.MONTH

class QuarterInterval(TimeInterval):

    def __init__(self, date : datetime.date):
        self.__year : int = date.year
        self.__quarter : int = ((date.month-1) // 3) + 1
    
    def __eq__(self, interval : object) -> bool:
        if isinstance(interval, QuarterInterval):
            return self.__year == interval.__year and self.__quarter == interval.__quarter
        else:
            return False
        
    def to_string(self) -> str:
        return f"{self.__year}-Q{self.__quarter}"
    
    @staticmethod
    def from_string(string : str) -> Optional[QuarterInterval]:
        match = re.search("^(\d{4})-Q(\d{1})$", string)
        if match:
            return QuarterInterval(datetime.date(year=int(match.group(1)), month=int(match.group(2))*3, day=1))
        else:
            return None

    def get_variant(self) -> TimeIntervalVariants:
        return TimeIntervalVariants.QUARTER

class HalfYearInterval(TimeInterval):

    def __init__(self, date : datetime.date):
        self.__year : int = date.year
        self.__half : int = ((date.month - 1) // 6) + 1

    def __eq__(self, interval : object) -> bool:
        if isinstance(interval, HalfYearInterval):
            return self.__year == interval.__year and self.__half == interval.__half
        else:
            return False

    def to_string(self) -> str:
        return f"{self.__year}-H{self.__half}"

    @staticmethod
    def from_string(string : str) -> Optional[HalfYearInterval]:
        match = re.search("^(\d{4})-H(\d{1})$", string)
        if match:
            return HalfYearInterval(datetime.date(year=int(match.group(1)), month=int(match.group(2))*6, day=1))
        else:
            return None
        
    def get_variant(self) -> TimeIntervalVariants:
        return TimeIntervalVariants.HALF_YEAR

class YearInterval(TimeInterval):

    def __init__(self, date : datetime.date):
        self.__year = date.year

    def __eq__(self, interval : object) -> bool:
        if isinstance(interval, YearInterval):
            return self.__year == interval.__year
        else:
            return False

    def to_string(self) -> str:
        return f"{self.__year}"
    
    @staticmethod
    def from_string(string : str) -> Optional[YearInterval]:
        match = re.search("^(\d{4})$", string)
        if match:
            return YearInterval(datetime.date(year=int(match.group(1)), month=1, day=1))
        else:
            return None
        
    def get_variant(self) -> TimeIntervalVariants:
        return TimeIntervalVariants.YEAR
