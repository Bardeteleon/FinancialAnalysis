from typing import Optional, Dict, Tuple
from user_interface.logger import logger
from data_types.Currency import CurrencyCode


class CurrencyConverter:

    def __init__(self, currency_config: Optional['CurrencyConfig']):
        self.__base_currency: Optional[CurrencyCode] = None
        self.__exchange_rates: Dict[Tuple[CurrencyCode, CurrencyCode], float] = {}

        if currency_config:
            self.__initialize_from_config(currency_config)

    def __initialize_from_config(self, currency_config):
        try:
            self.__base_currency = CurrencyCode(currency_config.base_currency)
        except ValueError:
            logger.error(f"Invalid base currency: {currency_config.base_currency}")
            return

        for rate_config in currency_config.exchange_rates:
            try:
                from_currency = CurrencyCode(rate_config.from_currency)
                to_currency = CurrencyCode(rate_config.to_currency)
                self.__exchange_rates[(from_currency, to_currency)] = rate_config.rate
            except ValueError as e:
                logger.warning(f"Invalid currency in exchange rate config: {e}")

    def convert(self, amount: float, from_currency: Optional[CurrencyCode]) -> float:
        if not self.__base_currency:
            return amount

        if from_currency is None:
            return amount

        if from_currency == self.__base_currency:
            return amount

        rate = self.__get_rate(from_currency, self.__base_currency)
        if rate is None:
            logger.error(
                f"No exchange rate for {from_currency.value} → {self.__base_currency.value}, using 1:1 rate"
            )
            return amount

        return amount * rate

    def __get_rate(self, from_currency: CurrencyCode, to_currency: CurrencyCode) -> Optional[float]:
        return self.__exchange_rates.get((from_currency, to_currency))

    def is_configured(self) -> bool:
        return self.__base_currency is not None

    def get_base_currency(self) -> Optional[CurrencyCode]:
        return self.__base_currency
