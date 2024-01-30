import logging
import re
from FinancialAnalysisInput import FinancialAnalysisInput
from data_types.Config import Config, read_config
from statement.EntryAugmentation import EntryAugmentation
from statement.EntrySorter import EntrySorter
from statement.EntryValidator import EntryValidator
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

class FinancialAnalysis:

    def __init__(self, input : FinancialAnalysisInput):
        self.__input : FinancialAnalysisInput = input

        logging.debug(f"Found {len(input.input_files)} input file")

        self.read_configs()

        self.__interpreted_entries_csv : List[InterpretedEntry] = []
        self.__interpreted_entries_pdf : List[InterpretedEntry] = []
        self.__augmented_entries_csv : List[InterpretedEntry] = []
    
    def read_configs(self):
        self.__config : Config = read_config(self.__input.config_json_file)
        self.__tags : TagConfig = load_tags(self.__input.tags_json_file)

    def interpret_csv_input(self):
        input_file_count = 1
        for input_file in self.__get_filtered_input_files("\.csv$"):

            logging.debug(f"{input_file_count}. {input_file}")
            input_file_count += 1

            csv_reader = CsvReader(input_file)
            csv_reader.run()

            raw_extractor = RawEntriesFromCsvExtractor(csv_reader.get_content(), self.__config)
            raw_extractor.run()

            interpreted_extractor = InterpretedStatementExtractor(raw_extractor.get_raw_entries(), self.__config, self.__tags)
            interpreted_extractor.run()
            self.__interpreted_entries_csv += interpreted_extractor.get_interpreted_entries()

    def interpret_pdf_input(self):
        input_file_count = 1
        for input_file in self.__get_filtered_input_files("\.pdf$"):

            logging.debug(f"{input_file_count}. {input_file}")
            input_file_count += 1

            pdf_reader = PdfReader(str(input_file))
            pdf_reader.run()

            raw_extractor = RawEntriesFromPdfTextExtractor(pdf_reader.get_text())
            raw_extractor.run()

            interpreted_extractor = InterpretedStatementExtractor(raw_extractor.get_raw_entries(), self.__config, self.__tags)
            interpreted_extractor.run()
            self.__interpreted_entries_pdf += interpreted_extractor.get_interpreted_entries()

    def validate_interpreted_input(self):
        logging.info("csv input validation")
        validator = EntryValidator([entry for entry in self.__interpreted_entries_csv if entry.raw.type != RawEntryType.UNKNOW])
        validator.validate_amounts_with_balances()
        logging.info("pdf input validation")
        validator = EntryValidator([entry for entry in self.__interpreted_entries_pdf if entry.raw.type != RawEntryType.UNKNOW])
        validator.validate_amounts_with_balances()

    def print_undefined_external_transaction_csv_entries(self):
        EntryPrinter.date_id_amount_tags_comment(
            EntrySorter.by_amount(
                EntryFilter.external_transactions(
                EntryFilter.undefined_transactions(
                    self.__interpreted_entries_csv
        ))))

    def augment_csv_entries(self):
        self.__augmented_entries_csv = EntryAugmentation.add_account_transactions_for_accounts_without_input_file_by_other_account_transactions(self.__interpreted_entries_csv, self.__config.internal_accounts)
        self.__augmented_entries_csv = EntryAugmentation.add_manual_balances(self.__augmented_entries_csv, self.__config.internal_accounts)

    def write_entries_to_csv(self):
        EntryWriter(self.__augmented_entries_csv).write_to_csv("interpreted_entries_csv.csv")
        EntryWriter(self.__interpreted_entries_pdf).write_to_csv("interpreted_entries_pdf.csv")

    def launce_interactive_overview(self):
        InteractiveOverviewTkinter(self.__augmented_entries_csv, self.__config, self.__tags)

    def __get_filtered_input_files(self, filter : str):
        return [file for file in self.__input.input_files if re.search(filter, file)]