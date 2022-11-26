import argparse
import os
import logging
from DataValidator import DataValidator
from InterpretedStatementExtractor import InterpretedStatementExtractor
from PdfReader import PdfReader
from RawStatementExtractor import RawStatementExtractor
from typing import List
from Types import *
from VisualizeStatement import VisualizeStatement
from InputPathInterpreter import InputPathInterpreter

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

    # print(pdf_reader.get_text())

    raw_extractor = RawStatementExtractor(pdf_reader.get_text())
    raw_extractor.run()

    # for entry in raw_extractor.get_raw_entries():
    #     print(entry)
    #     print("")
    # print(f"Count: {len(raw_extractor.get_raw_entries())}")

    interpreted_extractor = InterpretedStatementExtractor(raw_extractor.get_raw_entries())
    interpreted_extractor.load_tag_patterns("tags.json")
    interpreted_extractor.run()
    interpreted_entries += interpreted_extractor.get_interpreted_entries()

validator = DataValidator([entry for entry in interpreted_entries if entry.raw.type != StatementType.UNKNOW])
validation_successfull = validator.validate_amounts_with_balances()
if validation_successfull:
    logging.info("Validation OK!")
else:
    logging.warning("Validation failed!")

# for entry in interpreted_entries:
#     if len(entry.tags) == 0:
#         print(f"{entry.date} | {entry.amount} | {entry.raw.type} | {entry.raw.comment}")
#     else:
#         print(f"{entry.date} | {entry.amount} | {entry.raw.type} | {entry.tags}")
    # print(f"{entry.raw.date} -> {entry.date} | {entry.raw.amount} -> {entry.amount} | {entry.raw.comment}")

filterd_entries = [entry    for entry in interpreted_entries 
                            if      entry.raw.type == StatementType.TRANSACTION 
                                and Tag.ACCOUNT_SAVINGS not in entry.tags]

# VisualizeStatement.draw_amounts(filterd_entries)
# VisualizeStatement.draw_plus_minus_bar_per_month(filterd_entries)
