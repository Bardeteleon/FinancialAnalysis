import re
from Types import *
from typing import List

class InterpretedStatementExtractor:

    def __init__(self, raw_entries : List[RawEntry]):
        self.__raw_entries : List[RawEntry] = raw_entries

        self.__interpreted_entries : List[InterpretedEntry] = []
        self.__init_interpreted_entries()

    def run(self):
        self.__extract_amount()

    def get_interpreted_entries(self):
        return self.__interpreted_entries

    def __init_interpreted_entries(self):
        self.__interpreted_entries = [InterpretedEntry(date = None, amount = 0.0, tags = [], raw = raw_entry) for raw_entry in self.__raw_entries]

    def __extract_amount(self):
        for i, raw_entry in enumerate(self.__raw_entries):
            match = re.fullmatch("([\d\.]+),(\d{2}) ([HS])", raw_entry.amount)
            if match:
                before_comma : str = re.sub("\.", "", match.group(1))
                after_comma : str = match.group(2)
                plus_minus : str = match.group(3)

                self.__interpreted_entries[i].amount = float(int(before_comma))
                self.__interpreted_entries[i].amount += int(after_comma) / 100.0
                self.__interpreted_entries[i].amount *= -1 if plus_minus == "S" else +1
                