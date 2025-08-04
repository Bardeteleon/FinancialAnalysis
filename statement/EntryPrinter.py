from typing import List
from data_types.Types import InterpretedEntry
from data_types.Tag import UndefinedTag
from user_interface.logger import logger
from data_types.Types import InterpretedEntryType

class EntryPrinter:

    @staticmethod
    def count(entries : List[InterpretedEntry]):
        print(f"Count: {len(entries)}")

    @staticmethod
    def date_id_amount_tags_comment(entries : List[InterpretedEntry]):        
        for entry in entries:
            comment = entry.raw.comment if entry.raw else ""
            print(f"{entry.date} | {entry.account_id} | {entry.amount} |\t{entry.tags} | {comment}")
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

    @staticmethod
    def statistics(entries : List[InterpretedEntry]):
        total = len(entries)
        if total == 0:
            logger.info("No entries available to compute statistics.")
            return

        external = len([e for e in entries if e.type == InterpretedEntryType.TRANSACTION_EXTERNAL])
        internal = len([e for e in entries if e.type == InterpretedEntryType.TRANSACTION_INTERNAL])
        balances = len([e for e in entries if e.type == InterpretedEntryType.BALANCE])

        tagged = len([
            e for e in entries
            if e.is_tagged() and any(tag != UndefinedTag for tag in (e.tags or []))
        ])

        def percentage(value: int) -> float:
            return (value / total) * 100 if total else 0.0

        logger.info(f"Total entries: {total}")
        logger.info(f"  External transactions: {external} ({percentage(external):.1f}%)")
        logger.info(f"  Internal transactions: {internal} ({percentage(internal):.1f}%)")
        logger.info(f"  Balances: {balances} ({percentage(balances):.1f}%)")
        logger.info(f"Tagged entries: {tagged} ({percentage(tagged):.1f}%)")