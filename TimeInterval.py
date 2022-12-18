
import re
import datetime

from enum import Enum, auto

class TimeIntervalVariants(Enum):
    MONTH = auto()
    QUARTER = auto()
    HALF_YEAR = auto()
    YEAR = auto()

class TimeInterval:

    def __eq__(self, interval) -> bool:
        pass

    def to_string(self) -> str:
        pass

    @classmethod
    def from_string(cls, string : str):
        pass

    def get_variant(self) -> TimeIntervalVariants:
        pass

    @staticmethod
    def create(interval : TimeIntervalVariants, date : datetime.date):
        if interval == TimeIntervalVariants.MONTH:
            return MonthInterval(date)
        elif interval == TimeIntervalVariants.QUARTER:
            return QuarterInterval(date)
        elif interval == TimeIntervalVariants.HALF_YEAR:
            return HalfYearInterval(date)
        elif interval == TimeIntervalVariants.YEAR:
            return YearInterval(date)
        else:
            return None


class MonthInterval(TimeInterval):

    def __init__(self, date : datetime.date):
        self.__year : int = date.year
        self.__month : int = date.month

    def __eq__(self, interval) -> bool:
        return self.__year == interval.year and self.__month == interval.month

    def to_string(self) -> str:
        return f"{self.__year}-{self.__month}"
    
    @staticmethod
    def from_string(string : str):
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
    
    def __eq__(self, interval) -> bool:
        return self.__year == interval.year and self.__quarter == interval.quarter
        
    def to_string(self) -> str:
        return f"{self.__year}-Q{self.__quarter}"
    
    @staticmethod
    def from_string(string : str):
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

    def __eq__(self, interval) -> bool:
        return self.__year == interval.year and self.__half == interval.half

    def to_string(self) -> str:
        return f"{self.__year}-H{self.__half}"

    @staticmethod
    def from_string(string : str):
        match = re.search("^(\d{4})-H(\d{1})$", string)
        if match:
            return HalfYearInterval(datetime.date(year=int(match.group(1)), month=int(match.group(2)*6), day=1))
        else:
            return None
        
    def get_variant(self) -> TimeIntervalVariants:
        return TimeIntervalVariants.HALF_YEAR

class YearInterval(TimeInterval):

    def __init__(self, date : datetime.date):
        self.__year = date.year

    def __eq__(self, interval) -> bool:
        return self.__year == interval.year

    def to_string(self) -> str:
        return f"{self.__year}"
    
    @staticmethod
    def from_string(string : str):
        match = re.search("^(\d{4})$", string)
        if match:
            return YearInterval(datetime.date(year=int(match.group(1)), month=1, day=1))
        else:
            return None
        
    def get_variant(self) -> TimeIntervalVariants:
        return TimeIntervalVariants.YEAR
