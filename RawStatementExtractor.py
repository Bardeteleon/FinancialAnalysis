import re
from Types import *
from typing import List


class RawStatementExtractor:

    def __init__(self, statement_as_text : str):
        self.__statement_as_text : str = statement_as_text

        self.__year : str = ""
        self.__amounts : List[str] = []
        self.__dates : List[str] = []
        self.__entries : List[RawEntry] = []
    
    def run(self):
        self.__extract_year()
        self.__extract_dates()
        self.__extract_amounts()
        self.__init_entries_by_matching_amounts_with_dates()
        self.__extract_comments()
        self.__merge_year_with_dates()
    
    def get_raw_entries(self) -> List[RawEntry]:
        return self.__entries

    @staticmethod
    def __is_first_or_last_index(index : int, list : List) -> bool:
        return index == 0 or index == (len(list)-1)

    @staticmethod
    def __create_balance_entry(amount : str) -> RawEntry:
        return  RawEntry(
                    date = "",
                    amount = amount,
                    comment = "",
                    type = StatementType.BALANCE
                )

    def __extract_year(self):
        match = re.search("Nr\..+?\d+/(\d{4})", self.__statement_as_text)
        if match:
            self.__year = match.group(1)

    def __extract_dates(self):
        self.__dates = re.findall("\d{2}\.\d{2}\. \d{2}\.\d{2}\.", self.__statement_as_text)

    def __extract_amounts(self):
        self.__amounts = re.findall("\d[\d\.]*,\d{2} [HS]", self.__statement_as_text)

    def __init_entries_by_matching_amounts_with_dates(self):
        self.__entries : List[RawEntry] = []
        # Assumption 1: First entry is a Balance
        # Assumption 2: Equal amounts next to each other are Balances ~~~~
        date_index : int = 0
        for i, line in enumerate(self.__amounts):
            if RawStatementExtractor.__is_first_or_last_index(i, self.__amounts) or date_index == len(self.__dates):
                self.__entries.append(RawStatementExtractor.__create_balance_entry(line))
                if date_index == len(self.__dates): # TODO Find better solution for date/amount matching robustness
                    break
            elif line == self.__amounts[i-1] or line == self.__amounts[i+1]:
                self.__entries.append(RawStatementExtractor.__create_balance_entry(line))
            else:
                self.__entries.append(RawEntry(
                    date = self.__dates[date_index],
                    amount = line,
                    comment = "unknown",
                    type = StatementType.TRANSACTION
                ))
                date_index += 1

    def __extract_comments(self):
        shrinking_statement = self.__statement_as_text
        for i, statement in enumerate(self.__entries):
            if not RawStatementExtractor.__is_first_or_last_index(i, self.__entries) and statement.type is StatementType.TRANSACTION:
                start_phrase : str = statement.date
                end_phrase : str = ""
                if self.__entries[i+1].type is StatementType.TRANSACTION:
                    end_phrase = self.__entries[i+1].date
                else:
                    end_phrase = self.__entries[i+1].amount
                search_result = re.search(f"{re.escape(start_phrase)}.+?{re.escape(statement.amount)}.+?{re.escape(end_phrase)}", shrinking_statement)
                if search_result:
                    statement.comment = search_result.group(0)
                    shrinking_statement = shrinking_statement[(search_result.end(0)-len(end_phrase)):]

    def __merge_year_with_dates(self):
        for entry in self.__entries:
            entry.date = entry.date + self.__year