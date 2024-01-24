import re

from matplotlib.pyplot import text
from data_types.Types import *
from typing import List


class RawEntriesFromPdfTextExtractor:

    def __init__(self, statement_as_text : str):
        self.__statement_as_text : str = statement_as_text

        self.__year : str = ""
        self.__amounts : List[str] = []
        self.__dates : List[str] = []
        self.__entries : List[RawEntry] = []

        self.__amount_matches = []
        self.__text_in_front_of_amounts : List[str] = []
    
    def run(self):
        self.__extract_year()
        self.__extract_dates()
        self.__extract_amounts()
        self.__extract_text_in_front_of_amounts()
        self.__init_entries_with_amounts()
        self.__detect_if_amount_is_balance()
        self.__detect_if_amount_is_transaction_by_matching_with_dates()
        self.__extract_comments()
        self.__merge_year_with_dates()
    
    def get_raw_entries(self) -> List[RawEntry]:
        return self.__entries

    @staticmethod
    def __is_first_or_last_index(index : int, list : List) -> bool:
        return index == 0 or index == (len(list)-1)

    def __extract_year(self):
        match = re.search("Nr\..+?\d+/(\d{4})", self.__statement_as_text)
        if match:
            self.__year = match.group(1)

    def __extract_dates(self):
        self.__dates = re.findall("\d{2}\.\d{2}\. \d{2}\.\d{2}\.", self.__statement_as_text)

    def __extract_amounts(self):
        self.__amount_matches = list(re.finditer("\d[\d\.]*,\d{2} [HS]", self.__statement_as_text))
        for amount_match in self.__amount_matches:
            self.__amounts.append(amount_match.group(0))

    def __extract_text_in_front_of_amounts(self):
        last_amount_match_end = 0
        for amount_match in self.__amount_matches:    
            current_amont_match_end = amount_match.end(0)
            self.__text_in_front_of_amounts.append(self.__statement_as_text[last_amount_match_end:current_amont_match_end])
            last_amount_match_end = current_amont_match_end

    def __init_entries_with_amounts(self):
        for amount in self.__amounts:
            self.__entries.append(RawEntry(
                date = "",
                amount = amount,
                comment = "",
                account_idx=-1,
                type = RawEntryType.UNKNOW
            ))

    def __detect_if_amount_is_balance(self):
        for i, text_in_front_of_amount in enumerate(self.__text_in_front_of_amounts):
            balance_match = re.search(f"(alter Kontostand|neuer Kontostand|Übertrag auf|Übertrag von)", text_in_front_of_amount)
            if balance_match:
                self.__entries[i].comment = balance_match.group(1)
                self.__entries[i].type = RawEntryType.BALANCE

    def __detect_if_amount_is_transaction_by_matching_with_dates(self):
        date_index = 0
        for i, text_in_front_of_amount in enumerate(self.__text_in_front_of_amounts):
            date_match = re.search(f"{re.escape(self.__dates[date_index])}", text_in_front_of_amount)
            if date_match:
                self.__entries[i].date = self.__dates[date_index]
                self.__entries[i].type = RawEntryType.TRANSACTION
                date_index += 1
            if date_index >= len(self.__dates):
                break

    def __extract_comments(self):
        shrinking_statement = self.__statement_as_text
        for i, statement in enumerate(self.__entries):
            if not RawEntriesFromPdfTextExtractor.__is_first_or_last_index(i, self.__entries) and statement.type is RawEntryType.TRANSACTION:
                start_phrase : str = statement.date
                end_phrase : str = ""
                if self.__entries[i+1].type is RawEntryType.TRANSACTION:
                    end_phrase = self.__entries[i+1].date
                else:
                    end_phrase = self.__entries[i+1].amount
                search_result = re.search(f"{re.escape(start_phrase)}(.+?){re.escape(statement.amount)}(.+?){re.escape(end_phrase)}", shrinking_statement)
                if search_result:
                    statement.comment = search_result.group(1) + " " + search_result.group(2)
                    statement.comment = re.sub("\s+", " ", statement.comment)
                    shrinking_statement = shrinking_statement[(search_result.end(0)-len(end_phrase)):]

    def __merge_year_with_dates(self):
        for entry in self.__entries:
            entry.date = entry.date + self.__year