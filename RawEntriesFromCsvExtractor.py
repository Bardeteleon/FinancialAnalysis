from Types import *
from typing import *
import logging
import re

class RawEntriesFromCsvExtractor:

    def __init__(self, csv : List[List[str]]):
        self.__csv = csv
        
        self.__raw_entries : List[RawEntry] = []

    def run(self):
        if len(self.__csv) < 2:
            return

        index_date : int = self.__get_heading_index("Buchungstag")
        index_amount : int = self.__get_heading_index("Betrag")
        index_comment : int = self.__get_heading_index("Verwendungszweck")
        index_posting_text : int = self.__get_heading_index("Buchungstext")
        index_name_involved_person : int = self.__get_heading_index("Name Zahlungsbeteiligter")

        indentification_by_cell = self.__get_concatenated_cell_content([1], range(2))

        for row in self.__csv[1:]:
            raw_entry = RawEntry(
                date = row[index_date],
                amount = row[index_amount],
                comment = re.sub("\s+", " ", row[index_posting_text] + " " + row[index_name_involved_person] + " " + row[index_comment]),
                identification = indentification_by_cell,
                type = StatementType.TRANSACTION)
            self.__raw_entries.append(raw_entry)

        self.__raw_entries.reverse()

    def get_raw_entries(self) -> List[RawEntry]:
        return self.__raw_entries

    def __get_heading_index(self, heading : str) -> int:
        index : int = 0
        try:
            index = self.__csv[0].index(heading)
        except ValueError:
            logging.error(f"No {heading} index found in {self.__csv[0]}")
        return index

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