
from data_types.Types import InterpretedEntry, RawEntryType
from typing import *
import math
from user_interface.logger import logger

class EntryValidator:

    def __init__(self, interpreted_entries : List[InterpretedEntry]):
        self.__interpreted_entries = interpreted_entries

    def have_ascending_date_order(entries : List[InterpretedEntry]) -> bool:
        return EntryValidator.have_no_none_dates(entries) and all(entries[i].date <= entries[i+1].date for i in range(len(entries)-1))

    def have_no_none_dates(entries : List[InterpretedEntry]) -> bool:
        return all(entry.date is not None for entry in entries)

    def validate_amounts_with_balances(self) -> bool:
        # Positive validation assumption: From one balance all amounts some up to the value of the next balance.
        validation_successfull = True
        curr_start_balance_entry = None
        curr_end_balance_entry = None
        curr_sum = 0.0
        for entry in self.__interpreted_entries:
            if entry.raw.type == RawEntryType.BALANCE:
                if curr_start_balance_entry == None:
                    curr_start_balance_entry = entry
                    curr_sum = curr_start_balance_entry.amount
                elif curr_end_balance_entry == None:
                    curr_end_balance_entry = entry
            elif curr_start_balance_entry != None:
                curr_sum += entry.amount
            else:
                logger.debug(f"validate_amounts_with_balance: No validation for {entry}")
                validation_successfull = False

            if curr_start_balance_entry != None and curr_end_balance_entry != None:
                if math.isclose(curr_sum, curr_end_balance_entry.amount):
                    logger.debug(f"validate_amounts_with_balance: Fine between {curr_start_balance_entry.amount} and {curr_end_balance_entry.amount}")
                else:
                    logger.debug(f"validate_amounts_with_balance: Something is not ok between {curr_start_balance_entry.amount} and {curr_end_balance_entry.amount}")
                    validation_successfull = False
                curr_start_balance_entry = None
                curr_end_balance_entry = None
                curr_sum = 0.0
        if validation_successfull:
            logger.info("Validation OK!")
        else:
            logger.warning("Validation failed!")
        return validation_successfull
