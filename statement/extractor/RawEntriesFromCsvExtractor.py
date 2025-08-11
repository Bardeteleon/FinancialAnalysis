import os
from data_types.Types import *
from typing import *
from data_types.Config import Config
from file_reader.CsvReader import CsvReader
from user_interface.logger import logger
import re

@dataclass
class HeadingIndex:
    in_csv : int
    in_config : int

class RawEntriesFromCsvExtractor:

    def __init__(self, csv : CsvReader, config : Config, input_base_path : os.PathLike):
        self.__csv : CsvReader = csv
        self.__config : Config = config
        self.__input_base_path : os.PathLike = input_base_path

        self.__raw_entries : List[RawEntry] = []

    def run(self):
        if len(self.__csv.get_content()) < 2:
            logger.error("Csv not considered since too short")
            return

        self.__heading_index : Optional[HeadingIndex] = self.__find_heading_index() 
        if self.__heading_index is None:
            logger.error("No heading index found. Abort!")
            return

        self.__date_indices : List[Optional[int]] = [self.__find_column_index(column) for column in self.__config.headings[self.__heading_index.in_config].date]
        self.__amount_indices : List[Optional[int]] = [self.__find_column_index(column) for column in self.__config.headings[self.__heading_index.in_config].amount]
        self.__comment_indices : List[Optional[int]] = [self.__find_column_index(column) for column in self.__config.headings[self.__heading_index.in_config].comment]

        if None in self.__date_indices:
            logger.error("Unable to find all date columns")
            return
        if None in self.__amount_indices:
            logger.error("Unable to find all amount columns")
            return
        if None in self.__comment_indices:
            logger.error("Unable to find all comment columns")
            return

        self.__account_idx = self.__find_account_idx()

        if self.__account_idx == None:
            logger.error("No account found for input csv")
            return

        self.__extract_raw_entries()

    def get_raw_entries(self) -> List[RawEntry]:
        return self.__raw_entries

    def __extract_raw_entries(self):
        for row in self.__csv.get_content()[self.__heading_index.in_csv + 1:]:
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

        self.__raw_entries.reverse() # TODO Check if reverse is necessary by looking at dates


    def __find_column_index(self, column_heading : str) -> Optional[int]:
        for index, col in enumerate(self.__csv.get_content()[self.__heading_index.in_csv]):
            if re.search(re.escape(column_heading), col):
                return index
        logger.error(f"No column index found for '{column_heading}' in {self.__csv.get_content()[self.__heading_index.in_csv]}")
        return None

    def __find_heading_index(self) -> Optional[HeadingIndex]:
        for heading_index_in_config, heading_config in enumerate(self.__config.headings):
            all_column_headings : List[str] = []
            all_column_headings += heading_config.date
            all_column_headings += heading_config.amount
            all_column_headings += heading_config.comment
            all_column_headings = [re.escape(heading) for heading in all_column_headings]
            all_column_headings_regex = "(" + "|".join(all_column_headings) + ")"
            for heading_index_in_csv, row in enumerate(self.__csv.get_content()):
                row_as_string = " ".join(row)
                match = re.findall(all_column_headings_regex, row_as_string)
                if len(match) == len(all_column_headings):
                    logger.debug(f"Found heading config with index {heading_index_in_config} in row {heading_index_in_csv}")
                    return HeadingIndex(heading_index_in_csv, heading_index_in_config)
                if heading_index_in_csv > 10: # TODO Arbitrary break
                    break
        return None

    
    def __find_account_idx(self) -> Optional[int]:
        for account_idx, account in enumerate(self.__config.internal_accounts):
            if len(account.get_input_directory()) > 0:
                match_directory = re.search(re.escape(os.path.join(self.__input_base_path, account.get_input_directory())), self.__csv.get_input_file())
                if match_directory:
                    logger.debug(f"Matched csv file with account {account.get_name()}")
                    return account_idx
        return None

    def __get_concatenated_cell_content(self, rows : List[int], columns : List[int]) -> str:
        result : str = ""
        for row in rows:
            if row < len(self.__csv.get_content()):
                result += RawEntriesFromCsvExtractor.__get_concatenated_column_content(self.__csv.get_content()[row], columns)
        return result

    def __get_concatenated_column_content(column_data : List[str], column_indices : List[int]) -> str:
        if max(column_indices) < len(column_data):
            selected_columns = [column_data[selected_index] for selected_index in column_indices]
            return " ".join(selected_columns)

    def cleanup_whitespace(input : str) -> str:
        return re.sub(r'\s+', ' ', input).strip()