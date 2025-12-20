from datetime import date
from typing import List
from statement.EntryAugmentation import EntryAugmentation
from data_types.Config import Account, ManualBalance
from data_types.Types import InterpretedEntryType


def test_get_manual_balances_with_no_balance_references():
    accounts: List[Account] = [
        Account(
            name="Bank",
            transaction_iban="DE123",
            transaction_iban_alternative=None,
            input_directory="/some/path",
            balance_references=None
        )
    ]

    manual_balances = EntryAugmentation.get_manual_balances(accounts)

    assert len(manual_balances) == 0


def test_get_manual_balances_with_empty_balance_references_list():
    accounts: List[Account] = [
        Account(
            name="Bank",
            transaction_iban="DE123",
            transaction_iban_alternative=None,
            input_directory="/some/path",
            balance_references=[]
        )
    ]

    manual_balances = EntryAugmentation.get_manual_balances(accounts)

    assert len(manual_balances) == 0


def test_get_manual_balances_with_single_balance_reference():
    accounts: List[Account] = [
        Account(
            name="Bank",
            transaction_iban="DE123",
            transaction_iban_alternative=None,
            input_directory="/some/path",
            balance_references=[
                ManualBalance(date="2020-01-15", end_of_day_amount=1000.0)
            ]
        )
    ]

    manual_balances = EntryAugmentation.get_manual_balances(accounts)

    assert len(manual_balances) == 1
    assert manual_balances[0].date == date(2020, 1, 15)
    assert manual_balances[0].amount == 1000.0
    assert manual_balances[0].account_id == "DE123"
    assert manual_balances[0].type == InterpretedEntryType.BALANCE
    assert manual_balances[0].tags == []


def test_get_manual_balances_with_multiple_balance_references():
    accounts: List[Account] = [
        Account(
            name="Bank",
            transaction_iban="DE123",
            transaction_iban_alternative=None,
            input_directory="/some/path",
            balance_references=[
                ManualBalance(date="2020-01-15", end_of_day_amount=1000.0),
                ManualBalance(date="2020-02-15", end_of_day_amount=1500.0),
                ManualBalance(date="2020-03-15", end_of_day_amount=2000.0)
            ]
        )
    ]

    manual_balances = EntryAugmentation.get_manual_balances(accounts)

    assert len(manual_balances) == 3

    assert manual_balances[0].date == date(2020, 1, 15)
    assert manual_balances[0].amount == 1000.0
    assert manual_balances[0].account_id == "DE123"
    assert manual_balances[0].type == InterpretedEntryType.BALANCE

    assert manual_balances[1].date == date(2020, 2, 15)
    assert manual_balances[1].amount == 1500.0
    assert manual_balances[1].account_id == "DE123"
    assert manual_balances[1].type == InterpretedEntryType.BALANCE

    assert manual_balances[2].date == date(2020, 3, 15)
    assert manual_balances[2].amount == 2000.0
    assert manual_balances[2].account_id == "DE123"
    assert manual_balances[2].type == InterpretedEntryType.BALANCE


def test_get_manual_balances_with_multiple_accounts():
    accounts: List[Account] = [
        Account(
            name="Bank",
            transaction_iban="DE123",
            transaction_iban_alternative=None,
            input_directory="/some/path",
            balance_references=[
                ManualBalance(date="2020-01-15", end_of_day_amount=1000.0)
            ]
        ),
        Account(
            name="CreditCard",
            transaction_iban="DE456",
            transaction_iban_alternative=None,
            input_directory="/another/path",
            balance_references=[
                ManualBalance(date="2020-01-20", end_of_day_amount=-500.0)
            ]
        )
    ]

    manual_balances = EntryAugmentation.get_manual_balances(accounts)

    assert len(manual_balances) == 2

    bank_balances = [b for b in manual_balances if b.account_id == "DE123"]
    assert len(bank_balances) == 1
    assert bank_balances[0].amount == 1000.0
    assert bank_balances[0].date == date(2020, 1, 15)

    cc_balances = [b for b in manual_balances if b.account_id == "DE456"]
    assert len(cc_balances) == 1
    assert cc_balances[0].amount == -500.0
    assert cc_balances[0].date == date(2020, 1, 20)


def test_get_manual_balances_with_multiple_accounts_and_multiple_references():
    accounts: List[Account] = [
        Account(
            name="Bank",
            transaction_iban="DE123",
            transaction_iban_alternative=None,
            input_directory="/some/path",
            balance_references=[
                ManualBalance(date="2020-01-15", end_of_day_amount=1000.0),
                ManualBalance(date="2020-02-15", end_of_day_amount=1500.0)
            ]
        ),
        Account(
            name="CreditCard",
            transaction_iban="DE456",
            transaction_iban_alternative=None,
            input_directory="/another/path",
            balance_references=[
                ManualBalance(date="2020-01-20", end_of_day_amount=-500.0),
                ManualBalance(date="2020-02-20", end_of_day_amount=-600.0),
                ManualBalance(date="2020-03-20", end_of_day_amount=-700.0)
            ]
        ),
        Account(
            name="Savings",
            transaction_iban="DE789",
            transaction_iban_alternative=None,
            input_directory="/third/path",
            balance_references=None
        )
    ]

    manual_balances = EntryAugmentation.get_manual_balances(accounts)

    assert len(manual_balances) == 5

    bank_balances = [b for b in manual_balances if b.account_id == "DE123"]
    assert len(bank_balances) == 2
    assert bank_balances[0].amount == 1000.0
    assert bank_balances[1].amount == 1500.0

    cc_balances = [b for b in manual_balances if b.account_id == "DE456"]
    assert len(cc_balances) == 3
    assert cc_balances[0].amount == -500.0
    assert cc_balances[1].amount == -600.0
    assert cc_balances[2].amount == -700.0

    savings_balances = [b for b in manual_balances if b.account_id == "DE789"]
    assert len(savings_balances) == 0
