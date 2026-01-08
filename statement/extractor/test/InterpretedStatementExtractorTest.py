
from datetime import date
from typing import List

import pytest

from data_types.Config import Account, Config
from data_types.InterpretedEntry import InterpretedEntry, InterpretedEntryType
from data_types.RawEntry import RawEntry, RawEntryType
from statement.extractor.InterpretedStatementExtractor import InterpretedStatementExtractor


@pytest.fixture
def mock_account_a(mocker):
    account = mocker.MagicMock(spec=Account)
    account.get_id.return_value = 'Bank A'
    account.owner = ["Mr A"]
    return account

@pytest.fixture
def mock_account_b(mocker):
    account = mocker.MagicMock(spec=Account)
    account.get_id.return_value = 'Bank B'
    account.owner = ["Mr B"]
    return account

@pytest.fixture
def mock_account_c(mocker):
    account = mocker.MagicMock(spec=Account)
    account.get_id.return_value = 'Bank C'
    account.owner = ["Mr C"]
    return account

@pytest.fixture
def mock_config(mocker, mock_account_a, mock_account_b, mock_account_c):
    config = mocker.MagicMock(spec=Config)
    config.internal_accounts = [mock_account_a, mock_account_b, mock_account_c]
    return config

class TestExtractType:
    def test_internal_transactions_match_by_account_id(self, mock_config, mock_account_a, mock_account_b):
        entries: List[InterpretedEntry] = [
            InterpretedEntry(
                amount=-100.0,
                date=date(2020, 1, 5),
                raw=RawEntry(comment=f"X to {mock_account_b.get_id()}",
                             type=RawEntryType.TRANSACTION),
                account_id=mock_account_a.get_id()
            ),
            InterpretedEntry(
                amount=100.0,
                date=date(2020, 1, 5),
                raw=RawEntry(comment=f"From {mock_account_a.get_id()}",
                             type=RawEntryType.TRANSACTION),
                account_id=mock_account_b.get_id()
            ),
        ]

        InterpretedStatementExtractor(entries, mock_config).run()

        assert all([entry.is_internal() for entry in entries])

    def test_internal_transactions_match_by_owner(self, mock_config, mock_account_a, mock_account_b):
        entries: List[InterpretedEntry] = [
            InterpretedEntry(
                amount=-200.0,
                date=date(2020, 2, 10),
                raw=RawEntry(comment=f"Transfer to Mr B",
                             type=RawEntryType.TRANSACTION),
                account_id=mock_account_a.get_id()
            ),
            InterpretedEntry(
                amount=200.0,
                date=date(2020, 2, 10),
                raw=RawEntry(comment=f"Transfer from Mr A",
                             type=RawEntryType.TRANSACTION),
                account_id=mock_account_b.get_id()
            ),
        ]

        InterpretedStatementExtractor(entries, mock_config).run()

        assert all([entry.is_internal() for entry in entries])

    def test_internal_transactions_cross_match_account_id_and_owner(self, mock_config, mock_account_a, mock_account_b):
        entries: List[InterpretedEntry] = [
            InterpretedEntry(
                amount=-150.0,
                date=date(2020, 3, 15),
                raw=RawEntry(comment=f"Payment to {mock_account_b.get_id()}",
                             type=RawEntryType.TRANSACTION),
                account_id=mock_account_a.get_id()
            ),
            InterpretedEntry(
                amount=150.0,
                date=date(2020, 3, 15),
                raw=RawEntry(comment=f"Payment from Mr A",
                             type=RawEntryType.TRANSACTION),
                account_id=mock_account_b.get_id()
            ),
        ]

        InterpretedStatementExtractor(entries, mock_config).run()

        assert all([entry.is_internal() for entry in entries])

    def test_external_transactions_match_with_virtual(self, mock_config, mock_account_a, mock_account_b):
        entries: List[InterpretedEntry] = [
            InterpretedEntry(
                amount=-150.0,
                date=date(2020, 3, 15),
                raw=RawEntry(comment=f"Payment to {mock_account_b.get_id()}",
                             type=RawEntryType.TRANSACTION),
                account_id=mock_account_a.get_id()
            ),
            InterpretedEntry(
                amount=150.0,
                date=date(2020, 3, 15),
                type=InterpretedEntryType.TRANSACTION_INTERNAL,
                raw=None,
                account_id=mock_account_b.get_id()
            ),
        ]

        InterpretedStatementExtractor(entries, mock_config).run()

        assert all([entry.is_internal() for entry in entries])

    def test_external_transactions_only_one_way_reference_by_account_id(self, mock_config, mock_account_a, mock_account_b):
        entries: List[InterpretedEntry] = [
            InterpretedEntry(
                amount=-150.0,
                date=date(2020, 3, 15),
                raw=RawEntry(comment=f"Payment to {mock_account_b.get_id()}",
                             type=RawEntryType.TRANSACTION),
                account_id=mock_account_a.get_id()
            ),
            InterpretedEntry(
                amount=150.0,
                date=date(2020, 3, 15),
                raw=RawEntry(comment=f"Payment from someone",
                             type=RawEntryType.TRANSACTION),
                account_id=mock_account_b.get_id()
            ),
        ]

        InterpretedStatementExtractor(entries, mock_config).run()

        assert all([entry.is_internal() for entry in entries])

    def test_external_transactions_only_one_way_reference_by_owner(self, mock_config, mock_account_a, mock_account_b):
        entries: List[InterpretedEntry] = [
            InterpretedEntry(
                amount=-150.0,
                date=date(2020, 3, 15),
                raw=RawEntry(comment=f"Payment to {mock_account_b.owner}",
                             type=RawEntryType.TRANSACTION),
                account_id=mock_account_a.get_id()
            ),
            InterpretedEntry(
                amount=150.0,
                date=date(2020, 3, 15),
                raw=RawEntry(comment=f"Payment from someone",
                             type=RawEntryType.TRANSACTION),
                account_id=mock_account_b.get_id()
            ),
        ]

        InterpretedStatementExtractor(entries, mock_config).run()

        assert all([entry.is_external() for entry in entries])

    def test_external_transactions_no_match(self, mock_config, mock_account_a):
        entries: List[InterpretedEntry] = [
            InterpretedEntry(
                amount=-50.0,
                date=date(2020, 4, 20),
                raw=RawEntry(comment="Payment to external vendor",
                             type=RawEntryType.TRANSACTION),
                account_id=mock_account_a.get_id()
            ),
        ]

        InterpretedStatementExtractor(entries, mock_config).run()

        assert entries[0].is_external()

    def test_external_transactions_no_internal_reference(self, mock_config, mock_account_a, mock_account_b):
        entries: List[InterpretedEntry] = [
            InterpretedEntry(
                amount=-75.0,
                date=date(2020, 5, 25),
                raw=RawEntry(comment="External payment",
                             type=RawEntryType.TRANSACTION),
                account_id=mock_account_a.get_id()
            ),
            InterpretedEntry(
                amount=75.0,
                date=date(2020, 5, 25),
                raw=RawEntry(comment="Received from external",
                             type=RawEntryType.TRANSACTION),
                account_id=mock_account_b.get_id()
            ),
        ]

        InterpretedStatementExtractor(entries, mock_config).run()

        assert all([entry.is_external() for entry in entries])

    def test_internal_transactions_with_date_difference(self, mock_config, mock_account_a, mock_account_b):
        entries: List[InterpretedEntry] = [
            InterpretedEntry(
                amount=-300.0,
                date=date(2020, 6, 1),
                raw=RawEntry(comment=f"Transfer to {mock_account_b.get_id()}",
                             type=RawEntryType.TRANSACTION),
                account_id=mock_account_a.get_id()
            ),
            InterpretedEntry(
                amount=300.0,
                date=date(2020, 6, 4),
                raw=RawEntry(comment=f"Transfer from {mock_account_a.get_id()}",
                             type=RawEntryType.TRANSACTION),
                account_id=mock_account_b.get_id()
            ),
        ]

        InterpretedStatementExtractor(entries, mock_config).run()

        assert all([entry.is_internal() for entry in entries])

    def test_internal_transactions_with_too_big_date_difference(self, mock_config, mock_account_a, mock_account_b):
        entries: List[InterpretedEntry] = [
            InterpretedEntry(
                amount=-300.0,
                date=date(2020, 6, 1),
                raw=RawEntry(comment=f"Transfer to {mock_account_b.get_id()}",
                             type=RawEntryType.TRANSACTION),
                account_id=mock_account_a.get_id()
            ),
            InterpretedEntry(
                amount=300.0,
                date=date(2020, 6, 14),
                raw=RawEntry(comment=f"Transfer from {mock_account_a.get_id()}",
                             type=RawEntryType.TRANSACTION),
                account_id=mock_account_b.get_id()
            ),
        ]

        InterpretedStatementExtractor(entries, mock_config).run()

        assert all([entry.is_external() for entry in entries])

    def test_internal_transactions_with_amount_difference(self, mock_config, mock_account_a, mock_account_b):
        entries: List[InterpretedEntry] = [
            InterpretedEntry(
                amount=-300.0,
                date=date(2020, 6, 1),
                raw=RawEntry(comment=f"Transfer to {mock_account_b.get_id()}",
                             type=RawEntryType.TRANSACTION),
                account_id=mock_account_a.get_id()
            ),
            InterpretedEntry(
                amount=301.0,
                date=date(2020, 6, 1),
                raw=RawEntry(comment=f"Transfer from {mock_account_a.get_id()}",
                             type=RawEntryType.TRANSACTION),
                account_id=mock_account_b.get_id()
            ),
        ]

        InterpretedStatementExtractor(entries, mock_config).run()

        assert all([entry.is_external() for entry in entries])
