import logging
from datetime import date
from typing import List
from statement.EntryValidator import EntryValidator, BalanceValidationInterval
from data_types.Types import InterpretedEntry, InterpretedEntryType


def test_normal_case_transactions_between_balances():
    entries: List[InterpretedEntry] = [
        InterpretedEntry(
            amount=1000.0,
            account_id="Bank",
            type=InterpretedEntryType.BALANCE,
            date=date(2020, 1, 1)
        ),
        InterpretedEntry(
            amount=-50.0,
            account_id="Bank",
            type=InterpretedEntryType.TRANSACTION_INTERNAL,
            date=date(2020, 1, 2)
        ),
        InterpretedEntry(
            amount=100.0,
            account_id="Bank",
            type=InterpretedEntryType.TRANSACTION_EXTERNAL,
            date=date(2020, 1, 3)
        ),
        InterpretedEntry(
            amount=1050.0,
            account_id="Bank",
            type=InterpretedEntryType.BALANCE,
            date=date(2020, 1, 4)
        ),
    ]

    validator = EntryValidator(entries)
    intervals = validator.validate_amounts_with_balances()

    assert len(intervals) == 1
    interval = intervals[0]
    assert interval.account_id == "Bank"
    assert interval.start_date == date(2020, 1, 1)
    assert interval.end_date == date(2020, 1, 4)
    assert interval.start_balance == 1000.0
    assert interval.end_balance == 1050.0
    assert interval.calculated_sum == 1050.0
    assert interval.is_valid == True
    assert interval.entry_count == 2
    assert interval.is_unchecked == False
    assert interval.unchecked_reason == ""


def test_multiple_intervals_for_same_account():
    entries: List[InterpretedEntry] = [
        InterpretedEntry(
            amount=1000.0,
            account_id="Bank",
            type=InterpretedEntryType.BALANCE,
            date=date(2020, 1, 1)
        ),
        InterpretedEntry(
            amount=50.0,
            account_id="Bank",
            type=InterpretedEntryType.TRANSACTION_EXTERNAL,
            date=date(2020, 1, 2)
        ),
        InterpretedEntry(
            amount=1050.0,
            account_id="Bank",
            type=InterpretedEntryType.BALANCE,
            date=date(2020, 1, 3)
        ),
        InterpretedEntry(
            amount=-25.0,
            account_id="Bank",
            type=InterpretedEntryType.TRANSACTION_EXTERNAL,
            date=date(2020, 1, 4)
        ),
        InterpretedEntry(
            amount=1025.0,
            account_id="Bank",
            type=InterpretedEntryType.BALANCE,
            date=date(2020, 1, 5)
        ),
    ]

    validator = EntryValidator(entries)
    intervals = validator.validate_amounts_with_balances()

    assert len(intervals) == 2

    # First interval
    assert intervals[0].account_id == "Bank"
    assert intervals[0].start_balance == 1000.0
    assert intervals[0].end_balance == 1050.0
    assert intervals[0].is_valid == True
    assert intervals[0].entry_count == 1
    assert intervals[0].is_unchecked == False

    # Second interval
    assert intervals[1].account_id == "Bank"
    assert intervals[1].start_balance == 1050.0
    assert intervals[1].end_balance == 1025.0
    assert intervals[1].is_valid == True
    assert intervals[1].entry_count == 1
    assert intervals[1].is_unchecked == False


def test_multiple_accounts():
    entries: List[InterpretedEntry] = [
        # Bank account
        InterpretedEntry(
            amount=1000.0,
            account_id="Bank",
            type=InterpretedEntryType.BALANCE,
            date=date(2020, 1, 1),
        ),
        InterpretedEntry(
            amount=50.0,
            account_id="Bank",
            type=InterpretedEntryType.TRANSACTION_EXTERNAL,
            date=date(2020, 1, 2),
        ),
        InterpretedEntry(
            amount=1050.0,
            account_id="Bank",
            type=InterpretedEntryType.BALANCE,
            date=date(2020, 1, 3),
        ),
        # Credit card account
        InterpretedEntry(
            amount=0.0,
            account_id="CreditCard",
            type=InterpretedEntryType.BALANCE,
            date=date(2020, 1, 1),
        ),
        InterpretedEntry(
            amount=-100.0,
            account_id="CreditCard",
            type=InterpretedEntryType.TRANSACTION_EXTERNAL,
            date=date(2020, 1, 2),
        ),
        InterpretedEntry(
            amount=-100.0,
            account_id="CreditCard",
            type=InterpretedEntryType.BALANCE,
            date=date(2020, 1, 3),
        ),
    ]

    validator = EntryValidator(entries)
    intervals = validator.validate_amounts_with_balances()

    assert len(intervals) == 2

    # Bank interval
    bank_intervals = [i for i in intervals if i.account_id == "Bank"]
    assert len(bank_intervals) == 1
    assert bank_intervals[0].is_valid == True
    assert bank_intervals[0].entry_count == 1

    # Credit card interval
    cc_intervals = [i for i in intervals if i.account_id == "CreditCard"]
    assert len(cc_intervals) == 1
    assert cc_intervals[0].is_valid == True
    assert cc_intervals[0].entry_count == 1


def test_transactions_before_first_balance():
    entries: List[InterpretedEntry] = [
        InterpretedEntry(
            amount=-50.0,
            account_id="Bank",
            type=InterpretedEntryType.TRANSACTION_EXTERNAL,
            date=date(2020, 1, 1),
        ),
        InterpretedEntry(
            amount=100.0,
            account_id="Bank",
            type=InterpretedEntryType.TRANSACTION_EXTERNAL,
            date=date(2020, 1, 2),
        ),
        InterpretedEntry(
            amount=1000.0,
            account_id="Bank",
            type=InterpretedEntryType.BALANCE,
            date=date(2020, 1, 3),
        ),
        InterpretedEntry(
            amount=25.0,
            account_id="Bank",
            type=InterpretedEntryType.TRANSACTION_EXTERNAL,
            date=date(2020, 1, 4),
        ),
        InterpretedEntry(
            amount=1025.0,
            account_id="Bank",
            type=InterpretedEntryType.BALANCE,
            date=date(2020, 1, 5),
        ),
    ]

    validator = EntryValidator(entries)
    intervals = validator.validate_amounts_with_balances()

    assert len(intervals) == 2

    # First interval - unchecked (before first balance)
    assert intervals[0].account_id == "Bank"
    assert intervals[0].start_date == date(2020, 1, 1)
    assert intervals[0].end_date == date(2020, 1, 2)
    assert intervals[0].calculated_sum == 50.0  # -50 + 100
    assert intervals[0].is_valid == False
    assert intervals[0].is_unchecked == True
    assert intervals[0].unchecked_reason == "before_first_balance"
    assert intervals[0].entry_count == 2

    # Second interval - checked (between balances)
    assert intervals[1].account_id == "Bank"
    assert intervals[1].start_date == date(2020, 1, 3)
    assert intervals[1].end_date == date(2020, 1, 5)
    assert intervals[1].start_balance == 1000.0
    assert intervals[1].end_balance == 1025.0
    assert intervals[1].is_valid == True
    assert intervals[1].is_unchecked == False
    assert intervals[1].entry_count == 1


def test_transactions_after_last_balance():
    entries: List[InterpretedEntry] = [
        InterpretedEntry(
            amount=1000.0,
            account_id="Bank",
            type=InterpretedEntryType.BALANCE,
            date=date(2020, 1, 1),
        ),
        InterpretedEntry(
            amount=50.0,
            account_id="Bank",
            type=InterpretedEntryType.TRANSACTION_EXTERNAL,
            date=date(2020, 1, 2),
        ),
        InterpretedEntry(
            amount=1050.0,
            account_id="Bank",
            type=InterpretedEntryType.BALANCE,
            date=date(2020, 1, 3),
        ),
        InterpretedEntry(
            amount=-25.0,
            account_id="Bank",
            type=InterpretedEntryType.TRANSACTION_EXTERNAL,
            date=date(2020, 1, 4),
        ),
        InterpretedEntry(
            amount=100.0,
            account_id="Bank",
            type=InterpretedEntryType.TRANSACTION_EXTERNAL,
            date=date(2020, 1, 5),
        ),
    ]

    validator = EntryValidator(entries)
    intervals = validator.validate_amounts_with_balances()

    assert len(intervals) == 2

    # First interval - checked (between balances)
    assert intervals[0].account_id == "Bank"
    assert intervals[0].start_date == date(2020, 1, 1)
    assert intervals[0].end_date == date(2020, 1, 3)
    assert intervals[0].start_balance == 1000.0
    assert intervals[0].end_balance == 1050.0
    assert intervals[0].is_valid == True
    assert intervals[0].is_unchecked == False
    assert intervals[0].entry_count == 1

    # Second interval - unchecked (after last balance)
    assert intervals[1].account_id == "Bank"
    assert intervals[1].start_date == date(2020, 1, 3)
    assert intervals[1].end_date == date(2020, 1, 5)
    assert intervals[1].calculated_sum == 1125.0  # 1050 - 25 + 100
    assert intervals[1].is_valid == False
    assert intervals[1].is_unchecked == True
    assert intervals[1].unchecked_reason == "after_last_balance"
    assert intervals[1].entry_count == 2


def test_no_balances_at_all():
    entries: List[InterpretedEntry] = [
        InterpretedEntry(
            amount=-50.0,
            account_id="Bank",
            type=InterpretedEntryType.TRANSACTION_EXTERNAL,
            date=date(2020, 1, 1),
        ),
        InterpretedEntry(
            amount=100.0,
            account_id="Bank",
            type=InterpretedEntryType.TRANSACTION_EXTERNAL,
            date=date(2020, 1, 2),
        ),
        InterpretedEntry(
            amount=-25.0,
            account_id="Bank",
            type=InterpretedEntryType.TRANSACTION_EXTERNAL,
            date=date(2020, 1, 3),
        ),
    ]

    validator = EntryValidator(entries)
    intervals = validator.validate_amounts_with_balances()

    assert len(intervals) == 1

    # All transactions are unchecked (no balances)
    assert intervals[0].account_id == "Bank"
    assert intervals[0].start_date == date(2020, 1, 1)
    assert intervals[0].end_date == date(2020, 1, 3)
    assert intervals[0].calculated_sum == 25.0  # -50 + 100 - 25
    assert intervals[0].is_valid == False
    assert intervals[0].is_unchecked == True
    assert intervals[0].unchecked_reason == "no_balances"
    assert intervals[0].entry_count == 3


def test_invalid_interval_where_transaction_sum_does_not_match_balances():
    """Test detection of invalid interval where transactions don't match balance"""
    entries: List[InterpretedEntry] = [
        InterpretedEntry(
            amount=1000.0,
            account_id="Bank",
            type=InterpretedEntryType.BALANCE,
            date=date(2020, 1, 1),
        ),
        InterpretedEntry(
            amount=-50.0,
            account_id="Bank",
            type=InterpretedEntryType.TRANSACTION_EXTERNAL,
            date=date(2020, 1, 2),
        ),
        InterpretedEntry(
            amount=1000.0,  # Wrong! Should be 950.0
            account_id="Bank",
            type=InterpretedEntryType.BALANCE,
            date=date(2020, 1, 3),
        ),
    ]

    validator = EntryValidator(entries)
    intervals = validator.validate_amounts_with_balances()

    assert len(intervals) == 1

    # Interval should be invalid
    assert intervals[0].account_id == "Bank"
    assert intervals[0].start_balance == 1000.0
    assert intervals[0].end_balance == 1000.0
    assert intervals[0].calculated_sum == 950.0
    assert intervals[0].is_valid == False
    assert intervals[0].is_unchecked == False
    assert intervals[0].entry_count == 1


def test_empty_entries():
    entries: List[InterpretedEntry] = []

    validator = EntryValidator(entries)
    intervals = validator.validate_amounts_with_balances()

    assert len(intervals) == 0


def test_virtual_entries_are_included():
    """Test that virtual entries (without raw data) are included in validation"""
    entries: List[InterpretedEntry] = [
        InterpretedEntry(
            amount=1000.0,
            account_id="Bank",
            type=InterpretedEntryType.BALANCE,
            date=date(2020, 1, 1)
        ),
        InterpretedEntry(
            amount=50.0,
            account_id="Bank",
            type=InterpretedEntryType.TRANSACTION_EXTERNAL,
            date=date(2020, 1, 2)
        ),
        InterpretedEntry(
            amount=-25.0,  # Virtual entry (no raw)
            account_id="Bank",
            type=InterpretedEntryType.TRANSACTION_INTERNAL,
            date=date(2020, 1, 2)
        ),
        InterpretedEntry(
            amount=1025.0,
            account_id="Bank",
            type=InterpretedEntryType.BALANCE,
            date=date(2020, 1, 3)
        ),
    ]

    validator = EntryValidator(entries)
    intervals = validator.validate_amounts_with_balances()

    assert len(intervals) == 1

    # Virtual entry should be included, so 50.0 + (-25.0) = 25.0 should be counted
    assert intervals[0].calculated_sum == 1025.0
    assert intervals[0].is_valid == True
    assert intervals[0].entry_count == 2  # Both transactions counted


def test_balance_only_no_transactions():
    entries: List[InterpretedEntry] = [
        InterpretedEntry(
            amount=1000.0,
            account_id="Bank",
            type=InterpretedEntryType.BALANCE,
            date=date(2020, 1, 1),
        ),
        InterpretedEntry(
            amount=1000.0,
            account_id="Bank",
            type=InterpretedEntryType.BALANCE,
            date=date(2020, 1, 3),
        ),
    ]

    validator = EntryValidator(entries)
    intervals = validator.validate_amounts_with_balances()

    assert len(intervals) == 1

    # Should have valid interval with no transactions
    assert intervals[0].start_balance == 1000.0
    assert intervals[0].end_balance == 1000.0
    assert intervals[0].calculated_sum == 1000.0
    assert intervals[0].is_valid == True
    assert intervals[0].entry_count == 0
    assert intervals[0].is_unchecked == False
    

def test_balance_only_no_transactions_with_balance_mismatch():
    entries: List[InterpretedEntry] = [
        InterpretedEntry(
            amount=1000.0,
            account_id="Bank",
            type=InterpretedEntryType.BALANCE,
            date=date(2020, 1, 1),
        ),
        InterpretedEntry(
            amount=1001.0,
            account_id="Bank",
            type=InterpretedEntryType.BALANCE,
            date=date(2020, 1, 3),
        ),
    ]

    validator = EntryValidator(entries)
    intervals = validator.validate_amounts_with_balances()

    assert len(intervals) == 1

    # Should have valid interval with no transactions
    assert intervals[0].start_balance == 1000.0
    assert intervals[0].end_balance == 1001.0
    assert intervals[0].calculated_sum == 1000.0
    assert intervals[0].is_valid == False
    assert intervals[0].entry_count == 0
    assert intervals[0].is_unchecked == False
