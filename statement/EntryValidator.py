
from data_types.Config import Config
from data_types.InterpretedEntry import InterpretedEntry
from typing import *
import math
from user_interface.logger import logger
from dataclasses import dataclass
from datetime import date

@dataclass
class TransactionsWithBalancesValidationInterval:
    account_id: str
    start_date: date
    end_date: date
    start_balance: float
    end_balance: float
    calculated_sum: float
    is_valid: bool
    transaction_count: int
    is_unchecked: bool = False  # True if transactions couldn't be validated (no balances)
    unchecked_reason: str = ""  # Reason why unchecked: 'before_first_balance', 'after_last_balance', 'no_balances'

@dataclass 
class ValidationResults:
    transactions_with_balances: List[TransactionsWithBalancesValidationInterval]

class EntryValidator:

    def __init__(self, interpreted_entries : List[InterpretedEntry]):
        self.__interpreted_entries = interpreted_entries

    def have_ascending_date_order(entries : List[InterpretedEntry]) -> bool:
        return EntryValidator.have_no_none_dates(entries) and all(entries[i].date <= entries[i+1].date for i in range(len(entries)-1))

    def have_no_none_dates(entries : List[InterpretedEntry]) -> bool:
        return all(entry.date is not None for entry in entries)

    def validate_transactions_with_balances(self) -> List[TransactionsWithBalancesValidationInterval]:
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
            intervals = self._validate_transactions_with_balances_for_one_account(account_id, entries)
            all_intervals.extend(intervals)

        return all_intervals

    def _validate_transactions_with_balances_for_one_account(self, account_id: str, entries: List[InterpretedEntry]) -> List[TransactionsWithBalancesValidationInterval]:
        intervals = []
        curr_start_balance_entry = None
        curr_end_balance_entry = None
        curr_sum = 0.0
        transaction_count = 0

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

                        interval = TransactionsWithBalancesValidationInterval(
                            account_id=account_id,
                            start_date=first_date,
                            end_date=last_date,
                            start_balance=0.0,
                            end_balance=0.0,
                            calculated_sum=total_amount,
                            is_valid=False,
                            transaction_count=len(transactions_before_first_balance),
                            is_unchecked=True,
                            unchecked_reason="before_first_balance"
                        )
                        intervals.append(interval)

                    curr_start_balance_entry = entry
                    curr_sum = curr_start_balance_entry.amount
                    transaction_count = 0
                elif curr_end_balance_entry is None:
                    curr_end_balance_entry = entry
            elif curr_start_balance_entry is not None:
                curr_sum += entry.amount
                transaction_count += 1
            else:
                # Transaction before first balance
                transactions_before_first_balance.append(entry)

            if curr_start_balance_entry is not None and curr_end_balance_entry is not None:
                is_valid = math.isclose(curr_sum, curr_end_balance_entry.amount)

                interval = TransactionsWithBalancesValidationInterval(
                    account_id=account_id,
                    start_date=curr_start_balance_entry.date,
                    end_date=curr_end_balance_entry.date,
                    start_balance=curr_start_balance_entry.amount,
                    end_balance=curr_end_balance_entry.amount,
                    calculated_sum=curr_sum,
                    is_valid=is_valid,
                    transaction_count=transaction_count,
                    is_unchecked=False
                )
                intervals.append(interval)

                # Reset for next interval
                curr_start_balance_entry = curr_end_balance_entry
                curr_end_balance_entry = None
                curr_sum = curr_start_balance_entry.amount
                transaction_count = 0

        # Handle transactions after last balance
        if curr_start_balance_entry is not None and transaction_count > 0:
            # We have a start balance but no end balance, and some transactions
            # Create unchecked interval for transactions after last balance
            last_transaction_date = None
            for entry in reversed(entries):
                if entry.is_transaction():
                    last_transaction_date = entry.date
                    break

            interval = TransactionsWithBalancesValidationInterval(
                account_id=account_id,
                start_date=curr_start_balance_entry.date,
                end_date=last_transaction_date if last_transaction_date else curr_start_balance_entry.date,
                start_balance=curr_start_balance_entry.amount,
                end_balance=0.0,
                calculated_sum=curr_sum,
                is_valid=False,
                transaction_count=transaction_count,
                is_unchecked=True,
                unchecked_reason="after_last_balance"
            )
            intervals.append(interval)

        # Handle case with no balances at all
        if curr_start_balance_entry is None and transactions_before_first_balance:
            first_date = transactions_before_first_balance[0].date
            last_date = transactions_before_first_balance[-1].date
            total_amount = sum(t.amount for t in transactions_before_first_balance)

            interval = TransactionsWithBalancesValidationInterval(
                account_id=account_id,
                start_date=first_date,
                end_date=last_date,
                start_balance=0.0,
                end_balance=0.0,
                calculated_sum=total_amount,
                is_valid=False,
                transaction_count=len(transactions_before_first_balance),
                is_unchecked=True,
                unchecked_reason="no_balances"
            )
            intervals.append(interval)

        # self check if considered transactions equals amount of transactions
        all_transactions_in_entries = sum(1 for entry in entries if entry.is_transaction())
        all_transactions_in_intervals = sum(interval.transaction_count for interval in intervals)
        if all_transactions_in_entries != all_transactions_in_intervals:
            logger.error(f"Number of transactions in entries ({all_transactions_in_entries}) does not equal number of transactions in intervals ({all_transactions_in_intervals})")

        return intervals

    def validate(self) -> ValidationResults:
        return ValidationResults(transactions_with_balances=self.validate_transactions_with_balances())

    def calculate_sum_of_transactions(intervals : List[TransactionsWithBalancesValidationInterval]) -> int:
        return sum(interval.transaction_count for interval in intervals)

    @staticmethod
    def print_transactions_with_balances_validation_results(intervals: List[TransactionsWithBalancesValidationInterval], config : Optional[Config] = None):
        if not intervals:
            logger.info("No validation intervals to display")
            return
        
        logger.info("Transactions with balances validation:")

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

            account_name = f"{config.get_account_name(account_id)} / {account_id}" if config else f"{account_id}"
            logger.info(f"{'='*80}")
            logger.info(f"Account: {account_name}")
            logger.info(f"Summary: {EntryValidator.calculate_sum_of_transactions(valid_intervals)} valid, "
                        f"{EntryValidator.calculate_sum_of_transactions(invalid_intervals)} invalid, "
                        f"{EntryValidator.calculate_sum_of_transactions(unchecked_intervals)} unchecked transactions.")

            # Print invalid intervals
            if invalid_intervals:
                logger.error(f"  INVALID INTERVALS ({len(invalid_intervals)}):")
                for idx, interval in enumerate(invalid_intervals, 1):
                    difference = interval.calculated_sum - interval.end_balance
                    logger.error(f"    {idx}. {interval.start_date} to {interval.end_date}")
                    logger.error(f"       Start balance: {interval.start_balance:.2f}")
                    logger.error(f"       End balance:   {interval.end_balance:.2f}")
                    logger.error(f"       Calculated:    {interval.calculated_sum:.2f}")
                    logger.error(f"       Difference:    {difference:.2f}")
                    logger.error(f"       Transactions:  {interval.transaction_count}")

            # Print unchecked intervals
            if unchecked_intervals:
                logger.warning(f"  UNCHECKED INTERVALS ({len(unchecked_intervals)}):")
                for idx, interval in enumerate(unchecked_intervals, 1):
                    logger.warning(f"    {idx}. {interval.start_date} to {interval.end_date}")
                    logger.warning(f"       Reason:        {interval.unchecked_reason}")
                    logger.warning(f"       Transactions:  {interval.transaction_count}")
                    logger.warning(f"       Total amount:  {(interval.calculated_sum-interval.start_balance):.2f}")

        # Overall summary
        all_valid_intervals = [i for i in intervals if not i.is_unchecked and i.is_valid]
        all_valid_transactions = EntryValidator.calculate_sum_of_transactions(all_valid_intervals)
        all_invalid_intervals = [i for i in intervals if not i.is_unchecked and not i.is_valid]
        all_invalid_transactions = EntryValidator.calculate_sum_of_transactions(all_invalid_intervals)
        all_unchecked_intervals = [i for i in intervals if i.is_unchecked]
        all_unchecked_transactions = EntryValidator.calculate_sum_of_transactions(all_unchecked_intervals)

        logger.info(f"{'='*80}")
        logger.info(f"OVERALL SUMMARY")
        logger.info(f"{'='*80}")
        logger.info(f"Total accounts: {len(intervals_by_account)}")
        logger.info(f"Valid transactions:\t\t{all_valid_transactions}\t({len(all_valid_intervals)} intervals)")
        logger_fcn = logger.error if len(all_invalid_intervals) > 0 else logger.info
        logger_fcn(f"Invalid transactions:\t\t{all_invalid_transactions}\t({len(all_invalid_intervals)} intervals)")
        logger_fcn = logger.warning if len(all_unchecked_intervals) > 0 else logger.info
        logger_fcn(f"Unchecked transactions:\t{all_unchecked_transactions}\t({len(all_unchecked_intervals)} intervals)")
        logger.info(f"{'='*80}\n")

    @staticmethod
    def print_validation_results(results: ValidationResults, config : Optional[Config] = None):
        EntryValidator.print_transactions_with_balances_validation_results(results.transactions_with_balances, config)
