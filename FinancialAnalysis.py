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
from InputPathInterpreter import InputPathInterpreter
import matplotlib

print(matplotlib.get_backend())

logging.basicConfig(
    format="%(levelname)s %(asctime)s - %(message)s",
    level=logging.INFO
)

parser = argparse.ArgumentParser(prog="FinancialAnalysis")
parser.add_argument("input_path")
args = parser.parse_args()

path_interpreter = InputPathInterpreter(args.input_path)
path_interpreter.run()

interpreted_entries : List[InterpretedEntry] = []
for input_file in path_interpreter.get_input_files():

    pdf_reader = PdfReader(str(input_file))
    pdf_reader.run()

    raw_extractor = RawStatementExtractor(pdf_reader.get_text())
    raw_extractor.run()

    interpreted_extractor = InterpretedStatementExtractor(raw_extractor.get_raw_entries())
    interpreted_extractor.load_tag_patterns("tags.json")
    interpreted_extractor.run()
    interpreted_entries += interpreted_extractor.get_interpreted_entries()

validator = EntryValidator([entry for entry in interpreted_entries if entry.raw.type != StatementType.UNKNOW])
validator.validate_amounts_with_balances()

# EntryPrinter.date_amount_type_comment(EntrySorter.by_amount(EntryFilter.undefined_transactions(interpreted_entries)))

filtered_entries = EntryFilter.external_transactions(interpreted_entries)
# VisualizeStatement.draw_amounts(filtered_entries)
# VisualizeStatement.draw_balance_per_month(filtered_entries)
# VisualizeStatement.draw_tag_pie(datetime.date(2020, 8, 1), filtered_entries)
# VisualizeStatement.draw_overview(filtered_entries)
# VisualizeStatement.show()

InteractiveOverviewTkinter(filtered_entries)