from dataclasses import dataclass
from enum import Enum
from typing import Optional


class CurrencyCode(Enum):
    EUR = "EUR"
    USD = "USD"
    GBP = "GBP"
    CHF = "CHF"
    PLN = "PLN"
    JPY = "JPY"
    CAD = "CAD"
    AUD = "AUD"
    CNY = "CNY"
    INR = "INR"

# TODO unsued?
@dataclass
class CurrencyAmount:
    value: float
    currency: CurrencyCode

    def __str__(self):
        return f"{self.value:.2f} {self.currency.value}"


# TODO unsued?
@dataclass
class ExchangeRate:
    from_currency: CurrencyCode
    to_currency: CurrencyCode
    rate: float
    effective_date: Optional[str] = None
