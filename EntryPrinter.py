from ast import In
from typing import List
from Types import InterpretedEntry


class EntryPrinter:

    @staticmethod
    def date_amount_type_comment(entries : List[InterpretedEntry]):        
        for entry in entries:
            print(f"{entry.date} | {entry.amount} | {entry.raw.type} | {entry.raw.comment}")
        
    def date_amount_type_tags(entries : List[InterpretedEntry]):
        for entry in entries:
            print(f"{entry.date} | {entry.amount} | {entry.raw.type} | {entry.tags}")
    
    def raw_interpreted_comparison(entries : List[InterpretedEntry]):
        for entry in entries:
            print(f"{entry.raw.date} -> {entry.date} | {entry.raw.amount} -> {entry.amount} | {entry.raw.comment}")
