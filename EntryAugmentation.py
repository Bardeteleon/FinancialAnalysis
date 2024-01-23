
from datetime import date
from re import A
from sqlite3 import InternalError
from typing import List
from EntryFilter import EntryFilter
from EntryMapping import EntryMapping
from Types import CardType, InterpretedEntry, InterpretedEntryType
from Config import Account


class EntryAugmentation:
    
    @staticmethod
    def add_manual_balances(entries : List[InterpretedEntry], accounts : List[Account]) -> List[InterpretedEntry]:
        account_idx_to_id = EntryMapping.account_index_to_id(entries)
        for account_idx, account in enumerate(accounts):
            if account.balance_reference is not None:
                new_date = date.fromisoformat(account.balance_reference.date)
                account_id = account.transaction_iban if account.is_virtual() else account_idx_to_id[account_idx]
                new_entry = InterpretedEntry(date=new_date, 
                                             amount=account.balance_reference.end_of_day_amount, 
                                             account_id=account_id,
                                             type=InterpretedEntryType.BALANCE,
                                             tags=[])
                entries_len_before = len(entries)
                for entry_i, entry in enumerate(entries):
                    if    (   (entry.raw and entry.raw.account_idx == account_idx) \
                           or (entry.account_id == account_id)) \
                      and (entry.date > new_date):
                        entries.insert(entry_i, new_entry)
                        break
                if entries_len_before == len(entries):
                    entries.append(new_entry)
        return entries

    @staticmethod
    def add_account_transactions_for_accounts_without_input_file_by_other_account_transactions(all_entries : List[InterpretedEntry], all_accounts : List[Account]) -> List[InterpretedEntry]:
        new_entries = []
        for account in all_accounts:
            if account.input_file_identification is None:
                all_relevant_transactions = EntryFilter.transactions(all_entries, other_id=account.transaction_iban)
                for relevant_transaction in all_relevant_transactions:
                    new_entries.append(InterpretedEntry(
                        date=relevant_transaction.date,
                        amount=-1.0*relevant_transaction.amount,
                        tags=relevant_transaction.tags,
                        card_type=CardType.GIRO,
                        account_id=account.transaction_iban,
                        type=InterpretedEntryType.TRANSACTION_INTERNAL,
                        raw=None
                    ))
        all_entries += new_entries
        return all_entries