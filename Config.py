import dataconf
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class HeadingConfig:
    date : List[str]
    amount : List[str]
    comment : List[str]

@dataclass
class ManualBalance:
    date : str
    end_of_day_amount : float

@dataclass
class Account:
    name : str 
    transaction_iban : str
    input_file_identification : Optional[str]
    balance_reference : Optional[ManualBalance]

    def get_input_file_identification(self) -> str:
        return self.input_file_identification if self.input_file_identification else ""

    def is_virtual(self) -> bool:
        return self.input_file_identification is None

@dataclass
class CustomBalance:
    name : str
    plus : List[str]
    minus : List[str]

@dataclass
class Config:
    internal_accounts : List[Account]
    headings : List[HeadingConfig]
    custom_balances : Optional[List[CustomBalance]]

def read_config(file_path : str) -> Config:
    return dataconf.load(file_path, Config)
