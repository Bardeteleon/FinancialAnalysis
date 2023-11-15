from Types import InterpretedEntry
from typing import *
import csv

class EntryWriter:

    def __init__(self, entries : List[InterpretedEntry]):
        self.__entries = entries

    def write_to_csv(self, filepath : str):
        with open(filepath, "w", newline="") as file:
            csvwriter = csv.writer(file, quoting=csv.QUOTE_ALL)
            for entry in self.__entries:
                csvwriter.writerow([str(entry.date), str(entry.amount), str(entry.tags), str(entry.card_type), entry.account_id, str(entry.raw.type), entry.raw.comment])