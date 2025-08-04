from typing import List
from data_types.Types import InterpretedEntry
from data_types.Tag import UndefinedTag
from user_interface.logger import logger
from statement.EntryInsights import EntryInsights

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
        stats = EntryInsights.statistics(entries)

        def percentage(value: int) -> float:
            return (value / stats.total) * 100 if stats.total else 0.0

        logger.info(f"Total entries: {stats.total}")
        logger.info(f"  External transactions: {stats.external} ({percentage(stats.external):.1f}%)")
        logger.info(f"  Internal transactions: {stats.internal} ({percentage(stats.internal):.1f}%)")
        logger.info(f"  Balances: {stats.balances} ({percentage(stats.balances):.1f}%)")
        logger.info(f"Tagged entries: {stats.tagged} ({percentage(stats.tagged):.1f}%)")