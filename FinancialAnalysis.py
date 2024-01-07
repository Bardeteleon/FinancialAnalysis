import argparse
import os
import logging
import datetime
import tkinter
import csv
from Config import Config, read_config
from EntrySorter import EntrySorter
from EntryValidator import EntryValidator
from InteractiveOverviewTkinter import InteractiveOverviewTkinter
from InterpretedStatementExtractor import InterpretedStatementExtractor
from CsvReader import CsvReader
from PdfReader import PdfReader
from EntryPrinter import EntryPrinter
from EntryFilter import EntryFilter
from EntryWriter import EntryWriter
from RawEntriesFromCsvExtractor import RawEntriesFromCsvExtractor
from RawEntriesFromPdfTextExtractor import RawEntriesFromPdfTextExtractor
from typing import List
from tagging.TagConfig import TagConfig, load_tags
from Types import *
from VisualizeStatement import VisualizeStatement
from InputArgumentInterpreter import InputArgumentInterpreter

logging.basicConfig(
    format="%(levelname)s %(asctime)s - %(message)s",
    level=logging.INFO
)

parser = argparse.ArgumentParser(prog="FinancialAnalysis")
parser.add_argument("input_dir_path", help="Path to input directory where statements are stored.")
parser.add_argument("tags_json_path", help="Path to json file that defines patterns for tagging.")
parser.add_argument("config_json_path", help="Path to json file that defines various configs.")
args = parser.parse_args()

args_interpreter = InputArgumentInterpreter(args.input_dir_path, args.tags_json_path)
args_interpreter.run()

config : Config = read_config(args.config_json_path)
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

EntryPrinter.date_id_amount_tags_comment(
    EntrySorter.by_amount(
        EntryFilter.external_transactions(
        EntryFilter.undefined_transactions(
            interpreted_entries_csv
)
)))

InteractiveOverviewTkinter(interpreted_entries_csv, config, tags)

EntryWriter(interpreted_entries_csv).write_to_csv("interpreted_entries_csv.csv")
# EntryWriter(filtered_entries_pdf).write_to_csv("interpreted_entries_pdf.csv")

# EntryPrinter().raw_interpreted_comparison(filtered_entries_csv)