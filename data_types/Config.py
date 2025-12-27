import dataconf
from dataclasses import dataclass
from typing import List, Optional
from data_types.Currency import CurrencyCode
from user_interface.logger import logger

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
    transaction_iban_alternative : Optional[str] = None
    input_directory : Optional[str] = None
    balance_references : Optional[List[ManualBalance]] = None
    currency : Optional[str] = None

    def get_input_directory(self) -> str:
        return self.input_directory if self.input_directory else ""

    def is_virtual(self) -> bool:
        return self.input_directory is None

    def get_name(self) -> str:
        return self.name

    def get_id(self) -> str:
        return self.transaction_iban

    def get_currency_code(self) -> Optional[CurrencyCode]:
        if self.currency:
            try:
                return CurrencyCode(self.currency)
            except ValueError:
                logger.warning(f"Invalid currency code '{self.currency}' for account {self.name}")
        return None

@dataclass
class CustomBalance:
    name : str
    plus : List[str]
    minus : List[str]

@dataclass
class ExchangeRateConfig:
    from_currency : str
    to_currency : str
    rate : float

@dataclass
class CurrencyConfig:
    base_currency : str
    exchange_rates : List[ExchangeRateConfig]

@dataclass
class Config:
    internal_accounts : List[Account]
    headings : List[HeadingConfig]
    custom_balances : Optional[List[CustomBalance]] = None
    currency_config : Optional[CurrencyConfig] = None

def read_config(file_path : str) -> Config:
    return dataconf.load(file_path, Config)
