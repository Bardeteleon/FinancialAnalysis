import csv
import logging
from typing import List

class CsvReader:

    def __init__(self, input_file : str, delimiter : str = ";"):
        self.__input_file = input_file
        self.__delimiter = delimiter

        self.__content : List[List[str]] = []

    def run(self):    
        with open(self.__input_file, "r") as file:
            csv_reader = csv.reader(file, delimiter=self.__delimiter)
            for row in csv_reader:
                self.__content.append(row)
            logging.debug(f"Read {len(self.__content)} lines from csv")

    def get_content(self) -> List[List[str]]:
        return self.__content