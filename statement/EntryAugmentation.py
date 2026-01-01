
from datetime import date
import re
from typing import List, Optional
from statement.CurrencyConverter import CurrencyConverter
from statement.EntryFilter import EntryFilter
from data_types.InterpretedEntry import CardType, InterpretedEntry, InterpretedEntryType
from data_types.RawEntry import RawEntry
from data_types.Config import Account, CurrencyConfig


class EntryAugmentation:
    
    @staticmethod
    def get_manual_balances(internal_accounts : List[Account], currency_config : Optional[CurrencyConfig] = None) -> List[InterpretedEntry]:
        currency_converter : CurrencyConverter = CurrencyConverter(currency_config)
        manual_balances : List[InterpretedEntry] = []
        for account in internal_accounts:
            if account.balance_references is not None:
                for balance_reference in account.balance_references:
                    new_date = date.fromisoformat(balance_reference.date)
                    account_id = account.get_id()
                    account_currency = account.get_currency_code()
                    converted_amount = currency_converter.convert(balance_reference.end_of_day_amount, account_currency)
                    manual_balances.append(InterpretedEntry(
                                                 date=new_date,
                                                 amount=converted_amount,
                                                 original_amount=balance_reference.end_of_day_amount,
                                                 original_currency=account_currency,
                                                 converted_amount=converted_amount,
                                                 account_id=account_id,
                                                 type=InterpretedEntryType.BALANCE,
                                                 tags=[]))
        return manual_balances

    @staticmethod
    def get_account_transactions_for_accounts_without_input_file_by_other_account_transactions(all_entries : List[InterpretedEntry], all_accounts : List[Account]) -> List[InterpretedEntry]:
        new_entries = []
        for account in all_accounts:
            if account.is_virtual():
                all_relevant_transactions = EntryFilter.transactions(all_entries, other_id=account.get_id())
                for relevant_transaction in all_relevant_transactions:
                    new_entries.append(InterpretedEntry(
                        date=relevant_transaction.date,
                        amount=-1.0*relevant_transaction.amount,
                        original_amount=-1.0*relevant_transaction.original_amount,
                        original_currency=relevant_transaction.original_currency,
                        converted_amount=-1.0*relevant_transaction.converted_amount,
                        tags=relevant_transaction.tags,
                        card_type=CardType.GIRO,
                        account_id=account.get_id(),
                        type=InterpretedEntryType.TRANSACTION_INTERNAL,
                        raw=None
                    ))
        return new_entries

    @staticmethod
    def replace_alternative_transaction_iban_with_original(all_entries : List[RawEntry], all_accounts : List[Account]) -> List[RawEntry]:
        for account in all_accounts:
            if account.transaction_iban_alternative is not None:
                for entry in all_entries:
                    entry.comment = re.sub(account.transaction_iban_alternative, account.transaction_iban, entry.comment)
        return all_entries
