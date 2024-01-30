
import argparse

class InputArgumentParser:
    def __init__(self):
        self.__parser = argparse.ArgumentParser(prog="FinancialAnalysis", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        self.__parser.add_argument("--input_dir_path", help="Path to input directory where statements are stored.", default="input")
        self.__parser.add_argument("--tags_json_path", help="Path to json file that defines patterns for tagging.", default="tags.json")
        self.__parser.add_argument("--config_json_path", help="Path to json file that defines various configs.", default="config.json")

    def get_args(self):
        return self.__parser.parse_args()