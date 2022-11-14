import argparse
import os
from InterpretedStatementExtractor import InterpretedStatementExtractor
from PdfReader import PdfReader
from RawStatementExtractor import RawStatementExtractor
from typing import List
from Types import *
from VisualizeStatement import VisualizeStatement

parser = argparse.ArgumentParser(prog="FinancialAnalysis")
parser.add_argument("filename")

args = parser.parse_args()

test_file_path : os.PathLike = os.path.join(os.getcwd(), args.filename)

pdf_reader = PdfReader(str(test_file_path))
pdf_reader.run()

raw_extractor = RawStatementExtractor(pdf_reader.get_text())
raw_extractor.run()

# for entry in raw_extractor.get_raw_entries():
#     if entry.comment == "unknown":
#         print("UNKNOWN COMMENT:")
#     print(entry)
#     print("")
# print(f"Count: {len(raw_extractor.get_raw_entries())}")

interpreted_extractor = InterpretedStatementExtractor(raw_extractor.get_raw_entries())
interpreted_extractor.run()

for entry in interpreted_extractor.get_interpreted_entries():
    print(f"{entry.raw.date} -> {entry.date}")

# filterd_entries = [entry for entry in interpreted_extractor.get_interpreted_entries() if entry.raw.type == StatementType.TRANSACTION]

# VisualizeStatement.draw_amounts(filterd_entries)