from sre_parse import State
from Types import *
from typing import *
from Config import Config
import logging
import re

@dataclass
class HeadingIndex:
    in_csv : int
    in_config : int

class RawEntriesFromCsvExtractor:

    def __init__(self, csv : List[List[str]], config : Config):
        self.__csv = csv
        self.__config : Config = config
        self.__raw_entries : List[RawEntry] = []

    def run(self):
        if len(self.__csv) < 2:
            return

        self.__heading_index : Optional[HeadingIndex] = self.__find_heading_index() 
        if self.__heading_index is None:
            logging.error("No heading index found. Abort!")
            return

        self.__date_indices : List[Optional[int]] = [self.__find_column_index(column) for column in self.__config.headings[self.__heading_index.in_config].date]
        self.__amount_indices : List[Optional[int]] = [self.__find_column_index(column) for column in self.__config.headings[self.__heading_index.in_config].amount]
        self.__comment_indices : List[Optional[int]] = [self.__find_column_index(column) for column in self.__config.headings[self.__heading_index.in_config].comment]

        if None in self.__date_indices:
            logging.error("Unable to find all date columns")
            return
        if None in self.__amount_indices:
            logging.error("Unable to find all amount columns")
            return
        if None in self.__comment_indices:
            logging.error("Unable to find all comment columns")
            return

        self.__account_idx = self.__find_account_idx()

        self.__extract_raw_entries()

    def get_raw_entries(self) -> List[RawEntry]:
        return self.__raw_entries

    def __extract_raw_entries(self):
        for row in self.__csv[self.__heading_index.in_csv+1:]:
            raw_entry = RawEntry(
                date = RawEntriesFromCsvExtractor.__get_concatenated_column_content(row, self.__date_indices),
                amount = RawEntriesFromCsvExtractor.__get_concatenated_column_content(row, self.__amount_indices),
                comment = RawEntriesFromCsvExtractor.cleanup_whitespace(RawEntriesFromCsvExtractor.__get_concatenated_column_content(row, self.__comment_indices)),
                account_idx = self.__account_idx,
                type = RawEntryType.UNKNOW)
            if raw_entry.amount == "":
                continue
            if re.match("Tagessaldo", raw_entry.comment): # TODO Config
                raw_entry.type = RawEntryType.BALANCE
            else:
                raw_entry.type = RawEntryType.TRANSACTION
            self.__raw_entries.append(raw_entry)

        self.__raw_entries.reverse()


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
            all_column_headings = [re.escape(heading) for heading in all_column_headings]
            all_column_headings_regex = "(" + "|".join(all_column_headings) + ")"
            for heading_index_in_csv, row in enumerate(self.__csv):
                row_as_string = " ".join(row)
                match = re.findall(all_column_headings_regex, row_as_string)
                if len(match) == len(all_column_headings):
                    logging.debug(f"Found heading config with index {heading_index_in_config} in row {heading_index_in_csv}")
                    return HeadingIndex(heading_index_in_csv,heading_index_in_config)
                if heading_index_in_csv > 10:
                    break
        return None

    
    def __find_account_idx(self) -> str:
        for i, row in enumerate(self.__csv):
            row_as_string = " ".join(row)
            for account_idx, account in enumerate(self.__config.accounts):
                if len(account.input_file_ident) > 0:
                    match_name = re.search(re.escape(account.input_file_ident), row_as_string)
                    if match_name:
                        logging.debug(f"Found identification name in row {i} '{account.input_file_ident}'")
                        return account_idx

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

    def cleanup_whitespace(input : str) -> str:
        result : str = re.sub("\s+", " ", input)
        result = re.sub("^\s+", "", result)
        result = re.sub("\s+$", "", result)
        return str(result)