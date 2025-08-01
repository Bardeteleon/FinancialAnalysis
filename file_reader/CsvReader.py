import csv
import magic
from user_interface.logger import logger
from typing import List

class CsvReader:

    def __init__(self, input_file : str, delimiter : str = ";"):
        self.__input_file = input_file
        self.__delimiter = delimiter

        self.__content : List[List[str]] = []

    def run(self):
        with open(self.__input_file, "rb") as file:
            classification = magic.detect_from_content(file.read())
            logger.debug(f"Detected encoding: {classification.encoding}")
        with open(self.__input_file, "r", encoding=classification.encoding) as file:
            csv_reader = csv.reader(file, delimiter=self.__delimiter)
            for row in csv_reader:
                self.__content.append(row)
            logger.debug(f"Read {len(self.__content)} lines from csv")

    def get_content(self) -> List[List[str]]:
        return self.__content
    
    def get_input_file(self) -> str:
        return self.__input_file