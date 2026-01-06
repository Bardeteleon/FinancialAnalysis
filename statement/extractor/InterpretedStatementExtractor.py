from typing import List
from data_types.Config import Config
from data_types.InterpretedEntry import CardType, InterpretedEntry, InterpretedEntryType
from data_types.RawEntry import RawEntryType
from user_interface.logger import logger
import re

""" Extracts fields for interpreted entries that need consideration of the whole statement.
"""
class InterpretedStatementExtractor:
    def __init__(self, entries : List[InterpretedEntry], config : Config):
        self.__entries : List[InterpretedEntry] = entries
        self.__config : Config = config

    def run(self):
        self.__extract_type()

    def __extract_type(self):
        for entry in self.__entries:
            if entry.raw is None:
                if entry.type == InterpretedEntryType.UNKNOWN:
                    logger.warning(f"Entry has no raw data and unknown type. Unable to extract type. {entry}")
                else:
                    pass # keep type
            elif entry.raw.type == RawEntryType.BALANCE:
                entry.type = InterpretedEntryType.BALANCE
            elif entry.raw.type == RawEntryType.UNKNOW:
                entry.type = InterpretedEntryType.UNKNOWN
            elif entry.card_type == CardType.CREDIT:
                entry.type = InterpretedEntryType.TRANSACTION_INTERNAL if entry.amount > 0.0 else InterpretedEntryType.TRANSACTION_EXTERNAL
            else:
                all_internal_ibans_regex = "(" + "|".join(self.__get_internal_ibans()) + ")"
                match = re.search(all_internal_ibans_regex, entry.raw.comment)
                entry.type = InterpretedEntryType.TRANSACTION_INTERNAL if match else InterpretedEntryType.TRANSACTION_EXTERNAL

    def __get_internal_ibans(self) -> List[str]:
        return [account.transaction_iban for account in self.__config.internal_accounts]
