import csv
import magic
from user_interface.logger import logger
from typing import List

class CsvReader:

    def __init__(self, input_file : str):
        self.__input_file = input_file

        self.__content : List[List[str]] = []

    def run(self):
        with open(self.__input_file, "rb") as file:
            classification = magic.detect_from_content(file.read())
            logger.debug(f"Detected encoding: {classification.encoding}")
        with open(self.__input_file, "r", encoding=classification.encoding) as csv_file:
            csv_dialect = csv.Sniffer().sniff("".join(csv_file.readlines(1024)))
            csv_file.seek(0)
            csv_reader = csv.reader(csv_file, dialect=csv_dialect)
            for row in csv_reader:
                self.__content.append(row)
            logger.debug(f"Read {len(self.__content)} lines from csv")

    def get_content(self) -> List[List[str]]:
        return self.__content
    
    def get_input_file(self) -> str:
        return self.__input_file
