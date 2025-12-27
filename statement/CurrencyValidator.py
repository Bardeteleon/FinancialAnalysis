from typing import List, Set, Tuple
from data_types.Config import Config
from data_types.Currency import CurrencyCode

# TODO ConfigValidator
class CurrencyValidator:

    @staticmethod
    def validate_configuration(config: Config) -> List[str]:
        warnings : List[str] = []

        # TODO if no currency config check if all account currencies are the same

        if not config.currency_config:
            return warnings

        try:
            base_currency = CurrencyCode(config.currency_config.base_currency)
        except ValueError:
            warnings.append(f"Invalid base currency: {config.currency_config.base_currency}")
            return warnings

        required_currencies : Set[str] = set()

        for account in config.internal_accounts:
            if account.currency and account.currency != base_currency.value:
                try:
                    CurrencyCode(account.currency)
                    required_currencies.add(account.currency)
                except ValueError:
                    warnings.append(
                        f"Invalid currency '{account.currency}' for account {account.name}"
                    )
            # TODO warn if no currency defined but currency config exists

        available_rates : Set[Tuple[str, str]] = {
            (r.from_currency, r.to_currency)
            for r in config.currency_config.exchange_rates
        }

        for currency in required_currencies:
            if (currency, base_currency.value) not in available_rates:
                warnings.append(f"Missing exchange rate: {currency} → {base_currency.value}")

        return warnings
