from typing import List
from data_types.InterpretedEntry import InterpretedEntry


class Statement:

    def __init__(self, entries: List[InterpretedEntry]):
        self._entries = entries

    def get_entries(self) -> List[InterpretedEntry]:
        return self._entries
