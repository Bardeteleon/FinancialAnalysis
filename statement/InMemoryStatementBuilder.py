from typing import List, Optional
from data_types.Config import Config
from data_types.InterpretedEntry import InterpretedEntry
from statement.EntryMapping import EntryMapping
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

    """Build the Statement with entries sorted by date within each account_id."""
    def build(self) -> Statement:
        InterpretedStatementExtractor(self.__entries, self.__config).run()

        sorted_entries = []
        for _, entries in EntryMapping.entries_per_account(self.__entries).items():
            entries.sort(key=lambda entry: entry.date)
            sorted_entries.extend(entries)

        return Statement(sorted_entries)
