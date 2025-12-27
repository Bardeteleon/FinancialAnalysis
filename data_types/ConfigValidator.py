from typing import List, Set, Tuple
from data_types.Config import Config
from data_types.Currency import CurrencyCode

class ConfigValidator:

    @staticmethod
    def validate_currencies(config: Config) -> List[str]:
        warnings : List[str] = []

        required_currencies : Set[str] = set()
        for account in config.internal_accounts:
            if account.currency:
                try:
                    CurrencyCode(account.currency)
                    required_currencies.add(account.currency)
                except ValueError:
                    warnings.append(
                        f"Invalid currency '{account.currency}' for account '{account.name}'"
                    )
            elif config.currency_config:
                warnings.append(f"Missing currency for account '{account.name}'")

        if not config.currency_config:
            if len(required_currencies) > 1:
                warnings.append(f"Missing currency config. Detected different account currencies: {', '.join(required_currencies)}")
            return warnings

        try:
            base_currency = CurrencyCode(config.currency_config.base_currency)
        except ValueError:
            warnings.append(f"Invalid base currency: {config.currency_config.base_currency}")
            return warnings

        available_rates : Set[Tuple[str, str]] = {
            (r.from_currency, r.to_currency)
            for r in config.currency_config.exchange_rates
        }

        for currency in required_currencies:
            if currency == base_currency.value:
                continue
            if (currency, base_currency.value) not in available_rates:
                warnings.append(f"Missing exchange rate: {currency} → {base_currency.value}")

        return warnings
