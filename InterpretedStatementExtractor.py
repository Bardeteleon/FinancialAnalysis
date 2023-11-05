import re
import os
import datetime
import json
import logging
from Types import *
from typing import List


class InterpretedStatementExtractor:

    def __init__(self, raw_entries : List[RawEntry]):
        self.__raw_entries : List[RawEntry] = raw_entries

        self.__interpreted_entries : List[InterpretedEntry] = []
        self.__init_interpreted_entries()

        self.__tag_patterns : List[TagPattern] = []
    
    def load_tag_patterns(self, config_json : str):
        config_json_path = os.path.normpath(config_json)
        if not os.path.isfile(config_json_path):
            logging.warning(f"File {config_json_path} does not exist")
        else:
            with open(config_json_path, mode="r") as f:
                tag_patterns_json = json.load(f)
                if not isinstance(tag_patterns_json, List):
                    logging.warning(f"Expecting a list on first level inside {config_json_path}")
                for tag_pattern in tag_patterns_json:
                    self.__tag_patterns.append(
                        TagPattern(
                            pattern=tag_pattern["pattern"], 
                            tag=Tag[tag_pattern["tag"]] ) )

    def run(self):
        self.__extract_amount()
        self.__extract_date()
        self.__extract_tags()
        self.__add_undefined_tag_for_entries_without_tags()

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
                continue
            match = re.fullmatch("(-)*([\d]+)(,\d{1,2})", raw_entry.amount)
            if match:
                dotted_amount = re.sub(",", ".", raw_entry.amount)
                self.__interpreted_entries[i].amount = float(dotted_amount)
                continue
            
    
    def __extract_date(self):
        for i, raw_entry in enumerate(self.__raw_entries):
            match = re.fullmatch("(\d{2})\.(\d{2})\. \d{2}\.\d{2}\.(\d{4})", raw_entry.date)
            if match:
                day = int(match.group(1))
                month = int(match.group(2))
                year = int(match.group(3))
                self.__interpreted_entries[i].date = datetime.date(year, month, day)
            match = re.fullmatch("(\d{2})\.(\d{2})\.(\d{4})", raw_entry.date)
            if match:
                day = int(match.group(1))
                month = int(match.group(2))
                year = int(match.group(3))
                self.__interpreted_entries[i].date = datetime.date(year, month, day)

    def __extract_tags(self):
        for entry in self.__interpreted_entries:
            for tag_pattern in self.__tag_patterns:
                match = re.search(tag_pattern.pattern, entry.raw.comment)
                if match:
                    entry.tags.append(tag_pattern.tag)

    def __add_undefined_tag_for_entries_without_tags(self):
        for entry in self.__interpreted_entries:
            if len(entry.tags) == 0:
                entry.tags.append(Tag.UNDEFINED)