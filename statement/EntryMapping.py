from typing import Dict, List
from data_types.InterpretedEntry import InterpretedEntry

class EntryMapping:
    
    @staticmethod
    def account_index_to_id(entries : List[InterpretedEntry]) -> Dict[int, str]:
        return {entry.raw.account_idx : entry.account_id for entry in entries if entry.raw is not None}

    @staticmethod
    def entries_per_account(entries : List[InterpretedEntry]) -> Dict[str, List[InterpretedEntry]]:
        entries_per_account : Dict[str, List[InterpretedEntry]] = {}
        for entry in entries:
            if entry.account_id not in entries_per_account:
                entries_per_account[entry.account_id] = []
            entries_per_account[entry.account_id].append(entry)
        return entries_per_account
