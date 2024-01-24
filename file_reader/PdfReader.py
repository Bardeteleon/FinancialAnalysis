import PyPDF2
import re

class PdfReader:

    def __init__(self, file_path : str):
        self.__file_path : str = file_path
        self.__read_text : str  = ""

    def run(self):
        self.__read()
        self.__trim_whitespace()
    
    def get_text(self) -> str:
        return self.__read_text

    def __read(self):
        reader = PyPDF2.PdfReader(self.__file_path)
        for page in reader.pages:
            self.__read_text = self.__read_text + "\n" + page.extract_text()

    def __trim_whitespace(self):
        self.__read_text = re.sub("\s+", " ", self.__read_text)