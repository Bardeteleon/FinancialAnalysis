import logging
from datetime import date
from typing import List
from statement.EntryInsights import EntryInsights
from data_types.Types import InterpretedEntry, InterpretedEntryType


def test_balance_within_entries():
    entries : List[InterpretedEntry] = [
        InterpretedEntry(amount=-50.0, account_id="Bank", type=InterpretedEntryType.TRANSACTION_INTERNAL, date=date(2020, 1, 1)),
        InterpretedEntry(amount=100.0, account_id="Bank", type=InterpretedEntryType.TRANSACTION_EXTERNAL, date=date(2020, 1, 2)),
        InterpretedEntry(amount=1000.0, account_id="Bank", type=InterpretedEntryType.BALANCE, date=date(2020, 1, 3)),
        InterpretedEntry(amount=-33.0, account_id="Bank", type=InterpretedEntryType.TRANSACTION_INTERNAL, date=date(2020, 1, 4)),
    ]
    assert EntryInsights.initial_balance(entries, "Bank") == 950.0

def test_balance_at_last_position():
    entries : List[InterpretedEntry] = [
        InterpretedEntry(amount=-50.0, account_id="Bank", type=InterpretedEntryType.TRANSACTION_INTERNAL, date=date(2020, 1, 1)),
        InterpretedEntry(amount=100.0, account_id="Bank", type=InterpretedEntryType.TRANSACTION_EXTERNAL, date=date(2020, 1, 2)),
        InterpretedEntry(amount=1000.0, account_id="Bank", type=InterpretedEntryType.BALANCE, date=date(2020, 1, 3)),
    ]
    assert EntryInsights.initial_balance(entries, "Bank") == 950.0

def test_balance_at_first_position():
    entries : List[InterpretedEntry] = [
        InterpretedEntry(amount=1000.0, account_id="Bank", type=InterpretedEntryType.BALANCE, date=date(2020, 1, 1)),
        InterpretedEntry(amount=-50.0, account_id="Bank", type=InterpretedEntryType.TRANSACTION_INTERNAL, date=date(2020, 1, 1)),
        InterpretedEntry(amount=100.0, account_id="Bank", type=InterpretedEntryType.TRANSACTION_EXTERNAL, date=date(2020, 1, 1)),
    ]
    assert EntryInsights.initial_balance(entries, "Bank") == 1000.0

def test_no_balance_in_entries():
    entries : List[InterpretedEntry] = [
        InterpretedEntry(amount=-50.0, account_id="Bank", type=InterpretedEntryType.TRANSACTION_INTERNAL, date=date(2020, 1, 1)),
        InterpretedEntry(amount=100.0, account_id="Bank", type=InterpretedEntryType.TRANSACTION_EXTERNAL, date=date(2020, 1, 2)),
    ]
    assert EntryInsights.initial_balance(entries, "Bank") == 0.0

def test_not_ascending_date_order(caplog):
    caplog.set_level(logging.DEBUG)
    entries : List[InterpretedEntry] = [
        InterpretedEntry(amount=-50.0, account_id="Bank", type=InterpretedEntryType.TRANSACTION_INTERNAL, date=date(2020, 1, 2)),
        InterpretedEntry(amount=100.0, account_id="Bank", type=InterpretedEntryType.TRANSACTION_EXTERNAL, date=date(2020, 1, 3)),
        InterpretedEntry(amount=1000.0, account_id="Bank", type=InterpretedEntryType.BALANCE, date=date(2020, 1, 1)),
    ]
    assert EntryInsights.initial_balance(entries, "Bank") == 0.0
    assert "initial balance not derived" in caplog.text
