
from datetime import date
from typing import List
from EntryMapping import EntryMapping
from Types import InterpretedEntry, InterpretedEntryType
from Config import Account


class EntryAugmentation:
    
    @staticmethod
    def add_manual_balances(entries : List[InterpretedEntry], accounts : List[Account]) -> List[InterpretedEntry]:
        account_idx_to_id = EntryMapping.account_index_to_id(entries)
        for account_i, account in enumerate(accounts):
            if account.balance_reference is not None and account_i in account_idx_to_id:
                new_date = date.fromisoformat(account.balance_reference.date)
                new_entry = InterpretedEntry(date=new_date, 
                                             amount=account.balance_reference.end_of_day_amount, 
                                             account_id=account_idx_to_id[account_i],
                                             type=InterpretedEntryType.BALANCE,
                                             tags=[])
                entries_len_before = len(entries)
                for entry_i, entry in enumerate(entries):
                    if entry.raw and entry.raw.account_idx == account_i and entry.date > new_date:
                        entries.insert(entry_i, new_entry)
                        break
                if entries_len_before == len(entries):
                    entries.append(new_entry)
        return entries