
from data_types.Types import InterpretedEntry
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
            if entry.is_balance():
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
                if entry.is_transaction():
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

        return intervals

    @staticmethod
    def print_validation_results(intervals: List[BalanceValidationInterval]):
        if not intervals:
            logger.info("No validation intervals to display")
            return

        # Group intervals by account
        intervals_by_account = {}
        for interval in intervals:
            if interval.account_id not in intervals_by_account:
                intervals_by_account[interval.account_id] = []
            intervals_by_account[interval.account_id].append(interval)

        # Print results per account
        for account_id, account_intervals in intervals_by_account.items():
            valid_intervals = [i for i in account_intervals if not i.is_unchecked and i.is_valid]
            invalid_intervals = [i for i in account_intervals if not i.is_unchecked and not i.is_valid]
            unchecked_intervals = [i for i in account_intervals if i.is_unchecked]

            logger.info(f"\n{'='*80}")
            logger.info(f"Account: {account_id}")
            logger.info(f"{'='*80}")
            logger.info(f"Summary: {len(valid_intervals)} valid, {len(invalid_intervals)} invalid, {len(unchecked_intervals)} unchecked")

            # Print invalid intervals
            if invalid_intervals:
                logger.warning(f"\n  INVALID INTERVALS ({len(invalid_intervals)}):")
                for idx, interval in enumerate(invalid_intervals, 1):
                    difference = interval.calculated_sum - interval.end_balance
                    logger.warning(f"    {idx}. {interval.start_date} to {interval.end_date}")
                    logger.warning(f"       Start balance: {interval.start_balance:.2f}")
                    logger.warning(f"       End balance:   {interval.end_balance:.2f}")
                    logger.warning(f"       Calculated:    {interval.calculated_sum:.2f}")
                    logger.warning(f"       Difference:    {difference:.2f}")
                    logger.warning(f"       Transactions:  {interval.entry_count}")

            # Print unchecked intervals
            if unchecked_intervals:
                logger.warning(f"\n  UNCHECKED INTERVALS ({len(unchecked_intervals)}):")
                for idx, interval in enumerate(unchecked_intervals, 1):
                    logger.warning(f"    {idx}. {interval.start_date} to {interval.end_date}")
                    logger.warning(f"       Reason:        {interval.unchecked_reason}")
                    logger.warning(f"       Transactions:  {interval.entry_count}")
                    logger.warning(f"       Total amount:  {interval.calculated_sum:.2f}")

            # Summarize valid intervals
            if valid_intervals:
                logger.info(f"\n  VALID INTERVALS: {len(valid_intervals)}")
                total_transactions = sum(i.entry_count for i in valid_intervals)
                logger.info(f"    Total transactions validated: {total_transactions}")

        # Overall summary
        all_valid = [i for i in intervals if not i.is_unchecked and i.is_valid]
        all_invalid = [i for i in intervals if not i.is_unchecked and not i.is_valid]
        all_unchecked = [i for i in intervals if i.is_unchecked]

        logger.info(f"\n{'='*80}")
        logger.info(f"OVERALL SUMMARY")
        logger.info(f"{'='*80}")
        logger.info(f"Total accounts: {len(intervals_by_account)}")
        logger.info(f"Valid intervals: {len(all_valid)}")
        logger.info(f"Invalid intervals: {len(all_invalid)}")
        logger.info(f"Unchecked intervals: {len(all_unchecked)}")
        logger.info(f"{'='*80}\n")
