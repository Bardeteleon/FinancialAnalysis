import argparse
import os
import logging
import datetime
import tkinter
from EntrySorter import EntrySorter
from EntryValidator import EntryValidator
from InteractiveOverviewTkinter import InteractiveOverviewTkinter
from InterpretedStatementExtractor import InterpretedStatementExtractor
from PdfReader import PdfReader
from EntryPrinter import EntryPrinter
from EntryFilter import EntryFilter
from RawStatementExtractor import RawStatementExtractor
from typing import List
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
args = parser.parse_args()

args_interpreter = InputArgumentInterpreter(args.input_dir_path, args.tags_json_path)
args_interpreter.run()

interpreted_entries : List[InterpretedEntry] = []
for input_file in args_interpreter.get_input_files():

    pdf_reader = PdfReader(str(input_file))
    pdf_reader.run()

    raw_extractor = RawStatementExtractor(pdf_reader.get_text())
    raw_extractor.run()

    interpreted_extractor = InterpretedStatementExtractor(raw_extractor.get_raw_entries())
    interpreted_extractor.load_tag_patterns(args_interpreter.get_tags_json_file())
    interpreted_extractor.run()
    interpreted_entries += interpreted_extractor.get_interpreted_entries()

validator = EntryValidator([entry for entry in interpreted_entries if entry.raw.type != StatementType.UNKNOW])
validator.validate_amounts_with_balances()

# EntryPrinter.date_amount_type_comment(EntrySorter.by_amount(EntryFilter.undefined_transactions(interpreted_entries)))

filtered_entries = EntryFilter.external_transactions(interpreted_entries)

InteractiveOverviewTkinter(filtered_entries)