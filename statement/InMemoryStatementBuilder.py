from typing import List, Optional
from data_types.Config import Config
from data_types.InterpretedEntry import InterpretedEntry
from statement.Statement import Statement
from statement.extractor.InterpretedStatementExtractor import InterpretedStatementExtractor


class InMemoryStatementBuilder:

    def __init__(self, config : Config):
        self.__entries: List[InterpretedEntry] = []
        self.__config: Config = config

    def add_entries(self, entries: List[InterpretedEntry]) -> 'InMemoryStatementBuilder':
        self.__entries.extend(entries)
        return self

    def get_unsorted_entries(self) -> List[InterpretedEntry]:
        return self.__entries

    def build(self) -> Statement:
        InterpretedStatementExtractor(self.__entries, self.__config).run()

        """Build the Statement with entries sorted by date within each account_id."""
        # Group entries by account_id
        entries_by_account = {}
        for entry in self.__entries:
            account_id = entry.account_id
            if account_id not in entries_by_account:
                entries_by_account[account_id] = []
            entries_by_account[account_id].append(entry)

        # Sort entries by date within each account_id
        sorted_entries = []
        for account_id in entries_by_account:
            account_entries = entries_by_account[account_id]
            # Stable sort by date
            account_entries.sort(key=lambda entry: entry.date)
            sorted_entries.extend(account_entries)

        return Statement(sorted_entries)
