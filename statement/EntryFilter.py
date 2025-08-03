from copy import deepcopy
from typing import Callable, List, Dict, Optional, Set
from data_types.Config import CustomBalance
from data_types.Types import InterpretedEntry, InterpretedEntryType, RawEntryType
from data_types.Tag import Tag, UndefinedTag
import datetime
from user_interface.logger import logger
import re

from data_types.TagGroup import TagGroup

class EntryFilter:
    
    @staticmethod
    def formated_date(date : datetime.date) -> str:
        return f"{date.year}-{date.month}"

    @staticmethod
    def external_transactions(entries : List[InterpretedEntry]):
        return [entry for entry in entries 
                      if entry.type == InterpretedEntryType.TRANSACTION_EXTERNAL]
    @staticmethod
    def internal_transactions(entries : List[InterpretedEntry]):
        return [entry for entry in entries 
                      if entry.type == InterpretedEntryType.TRANSACTION_INTERNAL]

    @staticmethod
    def defined_transactions(entries : List[InterpretedEntry]):
        return [entry for entry in entries 
                      if entry.is_transaction() and entry.is_tagged() and (UndefinedTag not in entry.tags)]

    @staticmethod
    def undefined_transactions(entries : List[InterpretedEntry]):
        return [entry for entry in entries 
                      if     (entry.is_transaction())
                         and (entry.is_untagged() or UndefinedTag in entry.tags)]
    
    @staticmethod
    def positive_amount(entries : List[InterpretedEntry]):
        return [entry for entry in entries if entry.amount >= 0.0]
    
    @staticmethod
    def negative_amount(entries : List[InterpretedEntry]):
        return [entry for entry in entries if entry.amount < 0.0]

    @staticmethod
    def no_zero_amount(entries : List[InterpretedEntry]):
        return [entry for entry in entries if entry.amount != 0.0]

    @staticmethod
    def tag(entries : List[InterpretedEntry], given_tag : Tag):
        return [entry for entry in entries for tag in entry.tags if given_tag.contains(tag)]

    @staticmethod
    def transactions(entries : List[InterpretedEntry], main_id : Optional[str] = None, other_id : Optional[str] = None):
        return [entry for entry in entries if entry.is_transaction() and 
                                              (main_id is None or entry.account_id == main_id) and 
                                              (other_id is None or (entry.raw and re.search(other_id, entry.raw.comment)))]

    @staticmethod
    def from_to_date(entries : List[InterpretedEntry], from_date : datetime.date, to_date : datetime.date):
        return [entry for entry in entries if entry.date >= from_date and entry.date <= to_date]

    @staticmethod
    def custom_balance(balance_type_to_data : Dict[str, Callable], custom_balance : CustomBalance) -> List[InterpretedEntry]:

        def get_matches_in_a_list(input, list) -> List[str]:
            result = []
            for item in list:
                if re.search(re.escape(input), item):
                    result.append(item)
            return result

        result = []

        name_results = get_matches_in_a_list(custom_balance.name, custom_balance.plus + custom_balance.minus)
        if len(name_results) > 0:
            logger.error(f"Custom balance '{custom_balance.name}' contains itself in its definition (plus/minus).")
            return result

        for plus in custom_balance.plus:
            plus_results = get_matches_in_a_list(plus, balance_type_to_data.keys()) # TODO Allow multiple matches? Transactions can be duplicate in multiple balance types
            if len(plus_results) == 0:
                logger.warning(f"No match for custom balance '{custom_balance.name}' with plus '{plus}'")
            for plus_result in plus_results:
                result = result + balance_type_to_data[plus_result]()
        for minus in custom_balance.minus:
            minus_results = get_matches_in_a_list(minus, balance_type_to_data.keys()) # TODO Allow multiple matches? Transactions can be duplicate in multiple balance types
            if len(minus_results) == 0:
                logger.warning(f"No match for custom balance '{custom_balance.name}' with minus '{minus}'")
            for minus_result in minus_results:
                result = result + EntryFilter.reverse_sign_of_amounts(balance_type_to_data[minus_result]())
        return result

    @staticmethod
    def reverse_sign_of_amounts(entries : List[InterpretedEntry]) -> List[InterpretedEntry]:
        result = deepcopy(entries)
        for entry in result:
            entry.amount = -1 * entry.amount
        return result
    
    @staticmethod
    def account(entries : List[InterpretedEntry], account_id : str):
        return [entry for entry in entries if entry.account_id == account_id]
    
    @staticmethod
    def unique_accounts(entries : List[InterpretedEntry]) -> Set[str]:
        return {entry.account_id for entry in entries if len(entry.account_id) > 0}

    @staticmethod
    def non_virtual(entries : List[InterpretedEntry]) -> List[InterpretedEntry]:
        return [entry for entry in entries if not entry.is_virtual()]