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
    transaction_iban_alternative : Optional[str]
    input_directory : Optional[str]
    balance_references : Optional[List[ManualBalance]]

    def get_input_directory(self) -> str:
        return self.input_directory if self.input_directory else ""

    def is_virtual(self) -> bool:
        return self.input_directory is None
    
    def get_name(self) -> str:
        return self.name
    
    def get_id(self) -> str:
        return self.transaction_iban

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
