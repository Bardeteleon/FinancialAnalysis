import argparse
import os
import logging
import datetime
import sys
import tkinter
import csv
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
from user_interface.VisualizeStatement import VisualizeStatement
from user_interface.InputArgumentInterpreter import InputArgumentInterpreter

logging.basicConfig(
    format="%(levelname)s %(asctime)s - %(message)s",
    level=logging.INFO
)

parser = argparse.ArgumentParser(prog="FinancialAnalysis", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("--input_dir_path", help="Path to input directory where statements are stored.", default="input")
parser.add_argument("--tags_json_path", help="Path to json file that defines patterns for tagging.", default="tags.json")
parser.add_argument("--config_json_path", help="Path to json file that defines various configs.", default="config.json")
args = parser.parse_args()

args_interpreter = InputArgumentInterpreter(args.input_dir_path, args.tags_json_path, args.config_json_path)
args_interpreter.run()
if args_interpreter.has_error():
    sys.exit(1)

config : Config = read_config(args_interpreter.get_config_json_file())
tags : TagConfig = load_tags(args_interpreter.get_tags_json_file())

interpreted_entries_csv : List[InterpretedEntry] = []
interpreted_entries_pdf : List[InterpretedEntry] = []
logging.debug(f"Found {len(args_interpreter.get_input_files())} input file")
input_file_count = 1
for input_file in args_interpreter.get_filtered_input_files("\.csv$"):

    logging.debug(f"{input_file_count}. {input_file}")
    input_file_count += 1

    csv_reader = CsvReader(input_file)
    csv_reader.run()

    raw_extractor = RawEntriesFromCsvExtractor(csv_reader.get_content(), config)
    raw_extractor.run()

    interpreted_extractor = InterpretedStatementExtractor(raw_extractor.get_raw_entries(), config, tags)
    interpreted_extractor.run()
    interpreted_entries_csv += interpreted_extractor.get_interpreted_entries()

# for input_file in args_interpreter.get_filtered_input_files("\.pdf$"):

#     logging.debug(f"{input_file_count}. {input_file}")
#     input_file_count += 1

#     pdf_reader = PdfReader(str(input_file))
#     pdf_reader.run()

#     raw_extractor = RawEntriesFromPdfTextExtractor(pdf_reader.get_text())
#     raw_extractor.run()

#     interpreted_extractor = InterpretedStatementExtractor(raw_extractor.get_raw_entries(), config, tags)
#     interpreted_extractor.run()
#     interpreted_entries_pdf += interpreted_extractor.get_interpreted_entries()

# validator = EntryValidator([entry for entry in interpreted_entries if entry.raw.type != RawEntryType.UNKNOW])
# validator.validate_amounts_with_balances()

# EntryPrinter.date_id_amount_tags_comment(
#     EntrySorter.by_amount(
#         EntryFilter.external_transactions(
#         EntryFilter.undefined_transactions(
#             interpreted_entries_csv
# )
# )))

entries = EntryAugmentation.add_account_transactions_for_accounts_without_input_file_by_other_account_transactions(interpreted_entries_csv, config.internal_accounts)
entries = EntryAugmentation.add_manual_balances(entries, config.internal_accounts)

EntryWriter(entries).write_to_csv("interpreted_entries_csv.csv")
# EntryWriter(filtered_entries_pdf).write_to_csv("interpreted_entries_pdf.csv")

# EntryPrinter().raw_interpreted_comparison(filtered_entries_csv)

InteractiveOverviewTkinter(entries, config, tags)