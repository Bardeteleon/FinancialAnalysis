import dataconf
from dataclasses import dataclass
from typing import List

@dataclass
class HeadingConfig:
    date : List[str]
    amount : List[str]
    comment : List[str]

@dataclass
class Account:
    name : str 
    input_file_ident : str
    transaction_iban : str

@dataclass
class Config:
    accounts : List[Account]
    headings : List[HeadingConfig]

def read_config(file_path : str) -> Config:
    return dataconf.load(file_path, Config)
