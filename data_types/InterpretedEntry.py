from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Optional
from data_types.Tag import Tag
from data_types.Currency import CurrencyCode
from data_types.RawEntry import RawEntry
import datetime

class InterpretedEntryType(Enum):
    TRANSACTION_INTERNAL = auto()
    TRANSACTION_EXTERNAL = auto()
    BALANCE = auto()
    UNKNOWN = auto()

class CardType(Enum):
    CREDIT = auto()
    GIRO = auto()

@dataclass
class InterpretedEntry: # TODO update defaults
    date : datetime.date = datetime.date(1970, 1, 1)
    # TODO deprecated. Introduce get_amount
    amount : float = 0.0
    original_amount : float = 0.0
    original_currency : Optional[CurrencyCode] = None
    converted_amount : float = 0.0
    tags : List[Tag] = None
    card_type : CardType = None
    account_id : str = ""
    type : InterpretedEntryType = InterpretedEntryType.UNKNOWN
    raw : RawEntry = None
    internal_transaction_match : Optional['InterpretedEntry'] = None

    def is_untagged(self) -> bool:
        return self.tags is None or len(self.tags) == 0

    def is_tagged(self) -> bool:
        return not self.is_untagged()

    def is_transaction(self) -> bool:
        return self.type == InterpretedEntryType.TRANSACTION_EXTERNAL or \
               self.type == InterpretedEntryType.TRANSACTION_INTERNAL or \
               (self.raw is not None and self.raw.is_transaction())

    def is_balance(self) -> bool:
        return self.type == InterpretedEntryType.BALANCE or \
               (self.raw is not None and self.raw.is_balance())

    def is_virtual(self) -> bool:
        return self.raw is None
    
    def is_internal(self) -> bool:
        return self.type == InterpretedEntryType.TRANSACTION_INTERNAL
    
    def is_external(self) -> bool:
        return self.type == InterpretedEntryType.TRANSACTION_EXTERNAL

    def get_display_amount(self, base_currency: Optional[str] = None) -> str:
        if self.original_currency is None or self.original_currency.value == base_currency:
            return f"{self.amount:.2f}"
        return f"{self.converted_amount:.2f} (orig: {self.original_amount:.2f} {self.original_currency.value})"
