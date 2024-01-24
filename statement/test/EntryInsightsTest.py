
from typing import List
from statement.EntryInsights import EntryInsights
from data_types.Types import InterpretedEntry, InterpretedEntryType


def test_balance_within_entries():
    entries : List[InterpretedEntry] = [
        InterpretedEntry(amount=-50.0, account_id="Bank", type=InterpretedEntryType.TRANSACTION_INTERNAL),
        InterpretedEntry(amount=100.0, account_id="Bank", type=InterpretedEntryType.TRANSACTION_EXTERNAL),
        InterpretedEntry(amount=1000.0, account_id="Bank", type=InterpretedEntryType.BALANCE),
        InterpretedEntry(amount=-33.0, account_id="Bank", type=InterpretedEntryType.TRANSACTION_INTERNAL)
    ]
    assert EntryInsights.initial_balance(entries, "Bank") == 950.0

def test_balance_at_last_position():
    entries : List[InterpretedEntry] = [
        InterpretedEntry(amount=-50.0, account_id="Bank", type=InterpretedEntryType.TRANSACTION_INTERNAL),
        InterpretedEntry(amount=100.0, account_id="Bank", type=InterpretedEntryType.TRANSACTION_EXTERNAL),
        InterpretedEntry(amount=1000.0, account_id="Bank", type=InterpretedEntryType.BALANCE),
    ]
    assert EntryInsights.initial_balance(entries, "Bank") == 950.0

def test_balance_at_first_position():
    entries : List[InterpretedEntry] = [
        InterpretedEntry(amount=1000.0, account_id="Bank", type=InterpretedEntryType.BALANCE),
        InterpretedEntry(amount=-50.0, account_id="Bank", type=InterpretedEntryType.TRANSACTION_INTERNAL),
        InterpretedEntry(amount=100.0, account_id="Bank", type=InterpretedEntryType.TRANSACTION_EXTERNAL)
    ]
    assert EntryInsights.initial_balance(entries, "Bank") == 1000.0

def test_no_balance_in_entries():
    entries : List[InterpretedEntry] = [
        InterpretedEntry(amount=-50.0, account_id="Bank", type=InterpretedEntryType.TRANSACTION_INTERNAL),
        InterpretedEntry(amount=100.0, account_id="Bank", type=InterpretedEntryType.TRANSACTION_EXTERNAL)
    ]
    assert EntryInsights.initial_balance(entries, "Bank") == 0.0