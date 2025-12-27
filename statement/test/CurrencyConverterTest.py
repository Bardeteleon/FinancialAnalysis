from statement.CurrencyConverter import CurrencyConverter
from data_types.Currency import CurrencyCode
from data_types.Config import CurrencyConfig, ExchangeRateConfig


def test_convert_with_no_config():
    converter = CurrencyConverter(None)
    assert converter.convert(100.0, CurrencyCode.USD) == 100.0
    assert not converter.is_configured()


def test_convert_same_currency_as_base():
    config = CurrencyConfig(
        base_currency="EUR",
        exchange_rates=[]
    )
    converter = CurrencyConverter(config)
    assert converter.convert(100.0, CurrencyCode.EUR) == 100.0


def test_convert_with_exchange_rate():
    config = CurrencyConfig(
        base_currency="EUR",
        exchange_rates=[
            ExchangeRateConfig(from_currency="USD", to_currency="EUR", rate=0.92)
        ]
    )
    converter = CurrencyConverter(config)
    assert converter.convert(100.0, CurrencyCode.USD) == 92.0


def test_convert_with_missing_exchange_rate():
    config = CurrencyConfig(
        base_currency="EUR",
        exchange_rates=[]
    )
    converter = CurrencyConverter(config)
    assert converter.convert(100.0, CurrencyCode.USD) == 100.0
    # TODO check for error log


def test_convert_with_none_currency():
    config = CurrencyConfig(
        base_currency="EUR",
        exchange_rates=[]
    )
    converter = CurrencyConverter(config)
    assert converter.convert(100.0, None) == 100.0


def test_get_base_currency():
    config = CurrencyConfig(
        base_currency="EUR",
        exchange_rates=[]
    )
    converter = CurrencyConverter(config)
    assert converter.get_base_currency() == CurrencyCode.EUR
