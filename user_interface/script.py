import os
import sys
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from user_interface.InputArgumentInterpreter import InputArgumentInterpreter
from user_interface.InputArgumentParser import InputArgumentParser
from FinancialAnalysis import FinancialAnalysis

logging.basicConfig(
    format="%(levelname)s %(asctime)s - %(message)s",
    level=logging.INFO
)

args_parser = InputArgumentParser().get_args()

args_interpreter = InputArgumentInterpreter(args_parser.input_dir_path, 
                                            args_parser.tags_json_path, 
                                            args_parser.config_json_path)
args_interpreter.run()

analysis = FinancialAnalysis(args_interpreter.get_financial_analysis_input())
analysis.interpret_csv_input()
analysis.augment_csv_entries()
analysis.write_entries_to_csv()
analysis.launch_interactive_overview()
analysis.print_undefined_external_transaction_csv_entries()
