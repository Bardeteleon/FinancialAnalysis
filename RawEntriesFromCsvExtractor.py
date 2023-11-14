from Types import *
from typing import *
from Config import read_config, Config
import logging
import re

@dataclass
class HeadingIndex:
    in_csv : int
    in_config : int

class RawEntriesFromCsvExtractor:

    def __init__(self, csv : List[List[str]], config_json_path : str):
        self.__csv = csv
        self.__config_json_path : str = config_json_path
        self.__raw_entries : List[RawEntry] = []

    def run(self):
        if len(self.__csv) < 2:
            return

        self.__config : Config = read_config(self.__config_json_path)

        self.__heading_index : Optional[HeadingIndex] = self.__find_heading_index() 
        if self.__heading_index is None:
            logging.error("No heading index found. Abort!")
            return

        date_indices : List[Optional[int]] = [self.__find_column_index(column) for column in self.__config.headings[self.__heading_index.in_config].date]
        amount_indices : List[Optional[int]] = [self.__find_column_index(column) for column in self.__config.headings[self.__heading_index.in_config].amount]
        comment_indices : List[Optional[int]] = [self.__find_column_index(column) for column in self.__config.headings[self.__heading_index.in_config].comment]

        if None in date_indices:
            logging.error("Unable to find all date columns")
            return
        if None in amount_indices:
            logging.error("Unable to find all amount columns")
            return
        if None in comment_indices:
            logging.error("Unable to find all comment columns")
            return

        identification = self.__find_identification_by_name()

        for row in self.__csv[self.__heading_index.in_csv+1:]:
            raw_entry = RawEntry(
                date = RawEntriesFromCsvExtractor.__get_concatenated_column_content(row, date_indices),
                amount = RawEntriesFromCsvExtractor.__get_concatenated_column_content(row, amount_indices),
                comment = re.sub("\s+", " ", RawEntriesFromCsvExtractor.__get_concatenated_column_content(row, comment_indices)),
                identification = identification,
                type = StatementType.TRANSACTION)
            self.__raw_entries.append(raw_entry)

        self.__raw_entries.reverse()

    def get_raw_entries(self) -> List[RawEntry]:
        return self.__raw_entries

    def __find_column_index(self, column_heading : str) -> Optional[int]:
        index : Optional[int] = None
        try:
            index = self.__csv[self.__heading_index.in_csv].index(column_heading)
        except ValueError:
            logging.error(f"No {column_heading} index found in {self.__csv[self.__heading_index.in_csv]}")
        return index

    def __find_heading_index(self) -> Optional[HeadingIndex]:
        for heading_index_in_config, heading_config in enumerate(self.__config.headings):
            all_column_headings : List[str] = []
            all_column_headings += heading_config.date
            all_column_headings += heading_config.amount
            all_column_headings += heading_config.comment
            all_column_headings_regex = "(" + "|".join(all_column_headings) + f")"
            logging.debug(all_column_headings_regex)
            for heading_index_in_csv, row in enumerate(self.__csv):
                row_as_string = " ".join(row)
                match = re.findall(all_column_headings_regex, row_as_string)
                logging.debug(match)
                logging.debug(len(match))
                logging.debug(len(all_column_headings))
                if len(match) == len(all_column_headings):
                    return HeadingIndex(heading_index_in_csv,heading_index_in_config)
                if heading_index_in_csv > 10:
                    return None
        return None

    
    def __find_identification_by_name(self) -> str:
        for i, row in enumerate(self.__csv):
            row_as_string = " ".join(row)
            for name in self.__config.identifications:
                match_name = re.search(re.escape(name), row_as_string)
                if match_name:
                    logging.debug(f"Found identification name {name} in row {i}")
                    return name

    def __get_concatenated_cell_content(self, rows : List[int], columns : List[int]) -> str:
        result : str = ""
        for row in rows:
            if row < len(self.__csv):
                result += RawEntriesFromCsvExtractor.__get_concatenated_column_content(self.__csv[row], columns)
        return result

    def __get_concatenated_column_content(column_data : List[str], column_indices : List[int]) -> str:
        if max(column_indices) < len(column_data):
            selected_columns = [column_data[selected_index] for selected_index in column_indices]
            return " ".join(selected_columns)