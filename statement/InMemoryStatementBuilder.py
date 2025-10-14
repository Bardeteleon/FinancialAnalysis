from typing import List
from data_types.Types import InterpretedEntry
from statement.Statement import Statement


class InMemoryStatementBuilder:

    def __init__(self):
        self._entries: List[InterpretedEntry] = []

    def add_entries(self, entries: List[InterpretedEntry]) -> 'InMemoryStatementBuilder':
        self._entries.extend(entries)
        return self
    
    def get_unsorted_entries(self) -> List[InterpretedEntry]:
        return self._entries

    def build(self) -> Statement:
        """Build the Statement with entries sorted by date within each account_id."""
        # Group entries by account_id
        entries_by_account = {}
        for entry in self._entries:
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
