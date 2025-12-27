from data_types.ConfigValidator import ConfigValidator
from data_types.Config import Config, Account, HeadingConfig, CurrencyConfig, ExchangeRateConfig, ManualBalance


def test_validate_currencies_with_no_currency_config():
    config = Config(
        internal_accounts=[
            Account(
                name="Bank",
                transaction_iban="DE123",
            )
        ],
        currency_config=None
    )

    warnings = ConfigValidator.validate_currencies(config)

    assert len(warnings) == 0


def test_validate_currencies_with_valid_single_currency():
    config = Config(
        internal_accounts=[
            Account(
                name="Bank",
                transaction_iban="DE123",
                currency="EUR"
            )
        ],
        currency_config=CurrencyConfig(
            base_currency="EUR",
            exchange_rates=[]
        )
    )

    warnings = ConfigValidator.validate_currencies(config)

    assert len(warnings) == 0


def test_validate_currencies_with_valid_single_currency_without_currency_config():
    config = Config(
        internal_accounts=[
            Account(
                name="Bank1",
                transaction_iban="DE123",
                currency="EUR"
            ),
            Account(
                name="Bank2",
                transaction_iban="DE456",
                currency="EUR"
            )
        ],
        currency_config=None
    )

    warnings = ConfigValidator.validate_currencies(config)

    assert len(warnings) == 0


def test_validate_currencies_with_valid_multi_currency():
    config = Config(
        internal_accounts=[
            Account(
                name="EUR Bank",
                transaction_iban="DE123",
                currency="EUR"
            ),
            Account(
                name="USD Bank",
                transaction_iban="US456",
                currency="USD"
            ),
            Account(
                name="GBP Bank",
                transaction_iban="GB789",
                currency="GBP"
            )
        ],
        currency_config=CurrencyConfig(
            base_currency="EUR",
            exchange_rates=[
                ExchangeRateConfig(from_currency="USD", to_currency="EUR", rate=0.92),
                ExchangeRateConfig(from_currency="GBP", to_currency="EUR", rate=1.17)
            ]
        )
    )

    warnings = ConfigValidator.validate_currencies(config)

    assert len(warnings) == 0


def test_validate_currencies_with_invalid_base_currency():
    config = Config(
        internal_accounts=[
            Account(
                name="Bank",
                transaction_iban="DE123",
                currency="EUR"
            )
        ],
        currency_config=CurrencyConfig(
            base_currency="INVALID",
            exchange_rates=[]
        )
    )

    warnings = ConfigValidator.validate_currencies(config)

    assert len(warnings) == 1
    assert "Invalid base currency: INVALID" in warnings[0]


def test_validate_currencies_with_invalid_account_currency():
    config = Config(
        internal_accounts=[
            Account(
                name="Bank",
                transaction_iban="DE123",
                currency="INVALID"
            )
        ],
        currency_config=CurrencyConfig(
            base_currency="EUR",
            exchange_rates=[]
        )
    )

    warnings = ConfigValidator.validate_currencies(config)

    assert len(warnings) == 1
    assert "Invalid currency 'INVALID' for account 'Bank'" in warnings[0]


def test_validate_currencies_with_missing_exchange_rate():
    config = Config(
        internal_accounts=[
            Account(
                name="USD Bank",
                transaction_iban="US123",
                currency="USD"
            )
        ],
        currency_config=CurrencyConfig(
            base_currency="EUR",
            exchange_rates=[]
        )
    )

    warnings = ConfigValidator.validate_currencies(config)

    assert len(warnings) == 1
    assert "Missing exchange rate: USD → EUR" in warnings[0]


def test_validate_currencies_with_account_without_currency():
    config = Config(
        internal_accounts=[
            Account(
                name="EUR Bank",
                transaction_iban="DE123",
                currency="EUR"
            ),
            Account(
                name="No Currency Bank",
                transaction_iban="XX456",
                currency=None
            )
        ],
        currency_config=CurrencyConfig(
            base_currency="EUR",
            exchange_rates=[]
        )
    )

    warnings = ConfigValidator.validate_currencies(config)

    assert len(warnings) == 1
    assert "Missing currency for account 'No Currency Bank'" in warnings[0]


def test_validate_currencies_with_different_account_currencies_without_currency_config():
    config = Config(
        internal_accounts=[
            Account(
                name="EUR Bank",
                transaction_iban="DE123",
                currency="EUR"
            ),
            Account(
                name="USD Bank",
                transaction_iban="US456",
                currency="USD"
            )
        ],
        currency_config=None
    )

    warnings = ConfigValidator.validate_currencies(config)

    assert len(warnings) == 1
    assert "Missing currency config. Detected different account currencies: EUR, USD" in warnings[0] or \
           "Missing currency config. Detected different account currencies: USD, EUR" in warnings[0]


def test_validate_currencies_with_mixed_issues():
    config = Config(
        internal_accounts=[
            Account(
                name="Valid USD Bank",
                transaction_iban="US123",
                currency="USD"
            ),
            Account(
                name="Invalid Currency Bank",
                transaction_iban="XX456",
                currency="FAKE"
            ),
            Account(
                name="Missing Rate Bank",
                transaction_iban="GB789",
                currency="GBP"
            )
        ],
        currency_config=CurrencyConfig(
            base_currency="EUR",
            exchange_rates=[
                ExchangeRateConfig(from_currency="USD", to_currency="EUR", rate=0.92)
            ]
        )
    )

    warnings = ConfigValidator.validate_currencies(config)

    assert len(warnings) == 2
    assert any("Invalid currency 'FAKE' for account 'Invalid Currency Bank'" in w for w in warnings)
    assert any("Missing exchange rate: GBP → EUR" in w for w in warnings)
