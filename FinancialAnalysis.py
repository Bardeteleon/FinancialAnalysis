import argparse
import os
from InterpretedStatementExtractor import InterpretedStatementExtractor
from PdfReader import PdfReader
from RawStatementExtractor import RawStatementExtractor
from typing import List
from Types import *
from VisualizeStatement import VisualizeStatement
from InputPathInterpreter import InputPathInterpreter

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
    interpreted_extractor.run()
    interpreted_entries += interpreted_extractor.get_interpreted_entries()


# for entry in interpreted_entries:
#     print(f"{entry.date} | {entry.amount} | {entry.raw.type}")
    # print(f"{entry.raw.date} -> {entry.date} | {entry.raw.amount} -> {entry.amount} | {entry.raw.comment}")

filterd_entries = [entry for entry in interpreted_entries if entry.raw.type == StatementType.TRANSACTION]

VisualizeStatement.draw_amounts(filterd_entries)
VisualizeStatement.draw_plus_minus_bar_per_month(filterd_entries)