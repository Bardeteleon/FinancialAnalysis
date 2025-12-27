import datetime
import os
from user_interface.logger import logger
import re
from FinancialAnalysisInput import FinancialAnalysisInput
from data_types.Config import Config, read_config
from statement.EntryAugmentation import EntryAugmentation
from statement.EntrySorter import EntrySorter
from statement.EntryValidator import EntryValidator
from statement.CurrencyValidator import CurrencyValidator
from user_interface.InteractiveOverviewTkinter import InteractiveOverviewTkinter
from statement.extractor.InterpretedStatementExtractor import InterpretedStatementExtractor
from file_reader.CsvReader import CsvReader
from file_reader.PdfReader import PdfReader
from statement.EntryPrinter import EntryPrinter
from statement.EntryFilter import EntryFilter
from statement.EntryWriter import EntryWriter
from statement.extractor.RawEntriesFromCsvExtractor import RawEntriesFromCsvExtractor
from statement.extractor.RawEntriesFromPdfTextExtractor import RawEntriesFromPdfTextExtractor
from typing import List
from data_types.TagConfig import TagConfig, load_tags
from data_types.Types import *
from statement.Statement import Statement
from statement.InMemoryStatementBuilder import InMemoryStatementBuilder

class FinancialAnalysis:

    def __init__(self, input : FinancialAnalysisInput):
        self.__input : FinancialAnalysisInput = input

        self.__read_configs()

        self.__statement : Statement = None
    
    def __read_configs(self):
        self.__config : Config = read_config(self.__input.config_json_file)
        self.__tags : TagConfig = load_tags(self.__input.tags_json_file)
        self.__validate_currency_configuration()

    def read_and_interpret_input(self):
        statement_builder : InMemoryStatementBuilder = InMemoryStatementBuilder()
        self.__interpret_csv_input(statement_builder)
        self.__augment_csv_entries(statement_builder)
        # self.__interpret_pdf_input(statement_builder) # TODO no merge of data if overlap with csv exists
        self.__statement = statement_builder.build()

    def __interpret_csv_input(self, statement_builder : InMemoryStatementBuilder):
        input_file_count = 1
        for input_file in self.__get_filtered_input_files("\.csv$"):

            logger.debug(f"{input_file_count}. {input_file}")
            input_file_count += 1

            csv_reader = CsvReader(input_file)
            csv_reader.run()

            raw_extractor = RawEntriesFromCsvExtractor(csv_reader, self.__config, self.__input.input_base_path)
            raw_extractor.run()

            augmented_raw_entries = EntryAugmentation.replace_alternative_transaction_iban_with_original(raw_extractor.get_raw_entries(), self.__config.internal_accounts)

            interpreted_extractor = InterpretedStatementExtractor(augmented_raw_entries, self.__config, self.__tags)
            interpreted_extractor.run()
            statement_builder.add_entries(interpreted_extractor.get_interpreted_entries())

    def __augment_csv_entries(self, statement_builder : InMemoryStatementBuilder):
        statement_builder.add_entries(EntryAugmentation.get_account_transactions_for_accounts_without_input_file_by_other_account_transactions(statement_builder.get_unsorted_entries(), self.__config.internal_accounts))
        statement_builder.add_entries(EntryAugmentation.get_manual_balances(self.__config))

    def __interpret_pdf_input(self, statement_builder : InMemoryStatementBuilder):
        input_file_count = 1
        for input_file in self.__get_filtered_input_files("\.pdf$"):

            logger.debug(f"{input_file_count}. {input_file}")
            input_file_count += 1

            pdf_reader = PdfReader(str(input_file))
            pdf_reader.run()

            raw_extractor = RawEntriesFromPdfTextExtractor(pdf_reader.get_text())
            raw_extractor.run()

            interpreted_extractor = InterpretedStatementExtractor(raw_extractor.get_raw_entries(), self.__config, self.__tags)
            interpreted_extractor.run()
            statement_builder.add_entries(interpreted_extractor.get_interpreted_entries())

    def validate_interpreted_input(self):
        logger.info("")
        logger.info("Input validation:")
        validator = EntryValidator(self.__statement.get_entries())
        validation_intervals = validator.validate_amounts_with_balances()
        validator.print_validation_results(validation_intervals)

    def print_undefined_external_transaction_csv_entries(self):
        EntryPrinter.date_id_amount_tags_comment(
            # EntrySorter.by_date(
              EntrySorter.by_amount(
                EntryFilter.external_transactions(
                EntryFilter.undefined_transactions(
                    # EntryFilter.from_to_date(
                    self.__statement.get_entries()
                    # , datetime.date.fromisoformat("2023-06-01"), datetime.date.fromisoformat("2023-06-30"))
        ))
        ))

    def print_undefined_internal_transaction_csv_entries(self):
        EntryPrinter.date_id_amount_tags_comment(
            EntrySorter.by_amount(
                EntryFilter.internal_transactions(
                EntryFilter.undefined_transactions(
                    self.__statement.get_entries()
                )
                )
            )
        )

    def write_entries_to_csv(self):
        if not os.path.isdir(self.__get_export_file_path()):
            os.mkdir(self.__get_export_file_path())
        if len(self.__statement.get_entries()) > 0:
            EntryWriter(self.__statement.get_entries()).write_to_csv(self.__get_export_file_path("interpreted_entries.csv"))

    def launch_interactive_overview(self):
        InteractiveOverviewTkinter(self.__statement.get_entries(), self.__config, self.__tags)

    def print_entries_statistics(self):
        EntryPrinter.statistics(self.__statement.get_entries())

    def __get_filtered_input_files(self, filter : str):
        return [file for file in self.__input.input_files if re.search(filter, file)]
    
    def __get_export_file_path(self, file_name : str = ""):
        return os.path.join(self.__input.base_path, "export", file_name)

    def __validate_currency_configuration(self):
        warnings = CurrencyValidator.validate_configuration(self.__config)
        if warnings:
            logger.warning("Currency configuration warnings:")
            for warning in warnings:
                logger.warning(f"  - {warning}")
