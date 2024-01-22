
import logging
from typing import List, Optional
from EntryFilter import EntryFilter
from Types import InterpretedEntry, InterpretedEntryType

class EntryInsights:

    @staticmethod
    def initial_balance(entries : List[InterpretedEntry], account_id : str) -> float:
        result : float = 0.0
        account_entries = EntryFilter.account(entries, account_id)
        first_index_with_balance : Optional[int] = None
        for i, entry in enumerate(account_entries):
            if entry.type == InterpretedEntryType.BALANCE:
                first_index_with_balance = i
        if first_index_with_balance is not None:
            result = sum([ -1.0*entry.amount for entry in account_entries[:first_index_with_balance] if entry.is_transaction()])
            result += account_entries[first_index_with_balance].amount
        else:
            logging.debug(f"No entry with type balance found for accound id {account_id}")
        return result
    
    @staticmethod
    def initial_balance_if_entries_with_unique_account_unless_zero(entries : List[InterpretedEntry]) -> float:
        result : float = 0.0
        accounts = EntryFilter.unique_accounts(entries)
        if len(accounts) == 1: 
            account_id = accounts[0]
            initial_balance = EntryInsights.initial_balance(entries, account_id)
            logging.debug(f"Found only entries of account {account_id} with initial balance {initial_balance}")
        return result