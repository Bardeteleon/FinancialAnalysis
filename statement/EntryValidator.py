
from data_types.Types import InterpretedEntry, RawEntryType
from typing import *
import math
from user_interface.logger import logger
from dataclasses import dataclass
from datetime import date

@dataclass
class BalanceValidationInterval:
    account_id: str
    start_date: date
    end_date: date
    start_balance: float
    end_balance: float
    calculated_sum: float
    is_valid: bool
    entry_count: int
    is_unchecked: bool = False  # True if transactions couldn't be validated (no balances)
    unchecked_reason: str = ""  # Reason why unchecked: 'before_first_balance', 'after_last_balance', 'no_balances'

class EntryValidator:

    def __init__(self, interpreted_entries : List[InterpretedEntry]):
        self.__interpreted_entries = interpreted_entries

    def have_ascending_date_order(entries : List[InterpretedEntry]) -> bool:
        return EntryValidator.have_no_none_dates(entries) and all(entries[i].date <= entries[i+1].date for i in range(len(entries)-1))

    def have_no_none_dates(entries : List[InterpretedEntry]) -> bool:
        return all(entry.date is not None for entry in entries)

    def validate_amounts_with_balances(self) -> List[BalanceValidationInterval]:
        # Positive validation assumption: From one balance all amounts sum up to the value of the next balance.
        # Group entries by account_id
        entries_by_account = {}
        for entry in self.__interpreted_entries:
            if entry.account_id not in entries_by_account:
                entries_by_account[entry.account_id] = []
            entries_by_account[entry.account_id].append(entry)

        # Validate each account separately
        all_intervals = []
        for account_id, entries in entries_by_account.items():
            intervals = self._validate_account_balances(account_id, entries)
            all_intervals.extend(intervals)

        # Log summary
        total_intervals = len(all_intervals)
        checked_intervals = [i for i in all_intervals if not i.is_unchecked]
        unchecked_intervals = [i for i in all_intervals if i.is_unchecked]
        valid_intervals = sum(1 for interval in checked_intervals if interval.is_valid)
        invalid_intervals = sum(1 for interval in checked_intervals if not interval.is_valid)

        if unchecked_intervals:
            logger.warning(f"Validation: {valid_intervals} valid, {invalid_intervals} invalid, {len(unchecked_intervals)} unchecked intervals")
        elif total_intervals == valid_intervals:
            logger.info(f"Validation OK! {valid_intervals}/{total_intervals} intervals valid")
        else:
            logger.warning(f"Validation failed! {valid_intervals}/{total_intervals} intervals valid")

        return all_intervals

    def _validate_account_balances(self, account_id: str, entries: List[InterpretedEntry]) -> List[BalanceValidationInterval]:
        intervals = []
        curr_start_balance_entry = None
        curr_end_balance_entry = None
        curr_sum = 0.0
        entry_count = 0

        # Track transactions before first balance
        transactions_before_first_balance = []

        for entry in entries:
            # Skip virtual entries as they don't have raw type
            if entry.is_virtual():
                continue

            if entry.raw.type == RawEntryType.BALANCE:
                if curr_start_balance_entry is None:
                    # Found first balance - create unchecked interval for transactions before it
                    if transactions_before_first_balance:
                        first_date = transactions_before_first_balance[0].date
                        last_date = transactions_before_first_balance[-1].date
                        total_amount = sum(t.amount for t in transactions_before_first_balance)

                        interval = BalanceValidationInterval(
                            account_id=account_id,
                            start_date=first_date,
                            end_date=last_date,
                            start_balance=0.0,
                            end_balance=0.0,
                            calculated_sum=total_amount,
                            is_valid=False,
                            entry_count=len(transactions_before_first_balance),
                            is_unchecked=True,
                            unchecked_reason="before_first_balance"
                        )
                        intervals.append(interval)
                        logger.debug(f"validate_amounts_with_balance: {len(transactions_before_first_balance)} unchecked transactions before first balance for account {account_id}")

                    curr_start_balance_entry = entry
                    curr_sum = curr_start_balance_entry.amount
                    entry_count = 0
                elif curr_end_balance_entry is None:
                    curr_end_balance_entry = entry
            elif curr_start_balance_entry is not None:
                curr_sum += entry.amount
                entry_count += 1
            else:
                # Transaction before first balance
                transactions_before_first_balance.append(entry)

            if curr_start_balance_entry is not None and curr_end_balance_entry is not None:
                is_valid = math.isclose(curr_sum, curr_end_balance_entry.amount)

                interval = BalanceValidationInterval(
                    account_id=account_id,
                    start_date=curr_start_balance_entry.date,
                    end_date=curr_end_balance_entry.date,
                    start_balance=curr_start_balance_entry.amount,
                    end_balance=curr_end_balance_entry.amount,
                    calculated_sum=curr_sum,
                    is_valid=is_valid,
                    entry_count=entry_count,
                    is_unchecked=False
                )
                intervals.append(interval)

                if is_valid:
                    logger.debug(f"validate_amounts_with_balance: Fine for account {account_id} between {curr_start_balance_entry.amount} and {curr_end_balance_entry.amount}")
                else:
                    logger.debug(f"validate_amounts_with_balance: Something is not ok for account {account_id} between {curr_start_balance_entry.amount} and {curr_end_balance_entry.amount} (calculated: {curr_sum})")

                # Reset for next interval
                curr_start_balance_entry = curr_end_balance_entry
                curr_end_balance_entry = None
                curr_sum = curr_start_balance_entry.amount
                entry_count = 0

        # Handle transactions after last balance
        if curr_start_balance_entry is not None and entry_count > 0:
            # We have a start balance but no end balance, and some transactions
            # Create unchecked interval for transactions after last balance
            last_transaction_date = None
            for entry in reversed(entries):
                if not entry.is_virtual() and entry.raw.type != RawEntryType.BALANCE:
                    last_transaction_date = entry.date
                    break

            interval = BalanceValidationInterval(
                account_id=account_id,
                start_date=curr_start_balance_entry.date,
                end_date=last_transaction_date if last_transaction_date else curr_start_balance_entry.date,
                start_balance=curr_start_balance_entry.amount,
                end_balance=0.0,
                calculated_sum=curr_sum,
                is_valid=False,
                entry_count=entry_count,
                is_unchecked=True,
                unchecked_reason="after_last_balance"
            )
            intervals.append(interval)
            logger.debug(f"validate_amounts_with_balance: {entry_count} unchecked transactions after last balance for account {account_id}")

        # Handle case with no balances at all
        if curr_start_balance_entry is None and transactions_before_first_balance:
            first_date = transactions_before_first_balance[0].date
            last_date = transactions_before_first_balance[-1].date
            total_amount = sum(t.amount for t in transactions_before_first_balance)

            interval = BalanceValidationInterval(
                account_id=account_id,
                start_date=first_date,
                end_date=last_date,
                start_balance=0.0,
                end_balance=0.0,
                calculated_sum=total_amount,
                is_valid=False,
                entry_count=len(transactions_before_first_balance),
                is_unchecked=True,
                unchecked_reason="no_balances"
            )
            intervals.append(interval)
            logger.debug(f"validate_amounts_with_balance: {len(transactions_before_first_balance)} unchecked transactions (no balances) for account {account_id}")

        return intervals
