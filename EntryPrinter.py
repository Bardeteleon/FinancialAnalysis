from typing import List
from Types import InterpretedEntry

class EntryPrinter:

    @staticmethod
    def count(entries : List[InterpretedEntry]):
        print(f"Count: {len(entries)}")

    @staticmethod
    def date_id_amount_tags_comment(entries : List[InterpretedEntry]):        
        for entry in entries:
            print(f"{entry.date} | {entry.account_id} | {entry.amount} |\t{entry.tags} | {entry.raw.comment}")
        EntryPrinter.count(entries)

    @staticmethod
    def date_id_amount_type_comment(entries : List[InterpretedEntry]):        
        for entry in entries:
            print(f"{entry.date} | {entry.account_id} | {entry.amount} | \t{entry.raw.type} | {entry.raw.comment}")
        EntryPrinter.count(entries)
        
    @staticmethod
    def date_amount_type_tags(entries : List[InterpretedEntry]):
        for entry in entries:
            print(f"{entry.date} | {entry.amount} | {entry.raw.type} | {entry.tags}")
        EntryPrinter.count(entries)
    
    @staticmethod
    def raw_interpreted_comparison(entries : List[InterpretedEntry]):
        for entry in entries:
            print(f"{entry.raw.date} -> {entry.date} | {entry.raw.amount} -> {entry.amount} | {entry.raw.identification} -> {entry.card_type} & {entry.account_id}")
        EntryPrinter.count(entries)
