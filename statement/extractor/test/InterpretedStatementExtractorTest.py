import pytest
import datetime
from statement.extractor.InterpretedStatementExtractor import InterpretedStatementExtractor
from data_types.Config import Config, Account
from data_types.TagConfig import TagConfig
from data_types.Types import RawEntry, RawEntryType, InterpretedEntry

@pytest.fixture
def mock_config(mocker):
    account = mocker.MagicMock(spec=Account)
    account.get_input_directory.return_value = 'some/path'
    account.get_id.return_value = 'TEST_IBAN'
    account.transaction_iban = 'TEST_IBAN'

    config = mocker.MagicMock(spec=Config)
    config.internal_accounts = [account]
    return config

@pytest.fixture
def mock_tags(mocker):
    tags = mocker.MagicMock(spec=TagConfig)
    tags.tag_definitions = []
    return tags

@pytest.fixture
def make_raw_entry():
    """Factory function for creating RawEntry with sensible defaults"""
    def _make(date='01.01.2023', amount='100,00', comment='Test',
              account_idx=0, entry_type=RawEntryType.TRANSACTION):
        return RawEntry(date=date, amount=amount, comment=comment,
                       account_idx=account_idx, type=entry_type)
    return _make

@pytest.fixture
def run_extractor(mock_config, mock_tags):
    """Helper to run extractor and return interpreted entries"""
    def _run(raw_entries):
        extractor = InterpretedStatementExtractor(raw_entries, mock_config, mock_tags)
        extractor.run()
        return extractor.get_interpreted_entries()
    return _run


class TestExtractDate:
    """Tests for the __extract_date() method via the run() method."""

    @pytest.mark.parametrize("date_input,expected_date", [
        pytest.param('15.03. 15.03.2023', datetime.date(2023, 3, 15), id='dd_mm_space_format'),
        pytest.param('25.12.2023', datetime.date(2023, 12, 25), id='dd_mm_yyyy'),
        pytest.param('01.06.23', datetime.date(2023, 6, 1), id='dd_mm_yy'),
        pytest.param('31.12.00', datetime.date(2000, 12, 31), id='year_2000'),
        pytest.param('01.01.2024', datetime.date(2024, 1, 1), id='beginning_of_year'),
        pytest.param('31.12.2024', datetime.date(2024, 12, 31), id='end_of_year'),
        pytest.param('29.02.2024', datetime.date(2024, 2, 29), id='leap_year'),
        pytest.param('10.05. 15.05.2023', datetime.date(2023, 5, 10), id='space_format_different_dates'),
    ])
    def test_extract_date_valid_formats(self, date_input, expected_date,
                                       make_raw_entry, run_extractor):
        """Test date extraction for various valid formats"""
        raw_entries = [make_raw_entry(date=date_input)]
        result = run_extractor(raw_entries)
        assert result[0].date == expected_date

    @pytest.mark.parametrize("invalid_date,expected_log", [
        pytest.param('2023-03-15', "Could not extract date from: 2023-03-15", id='invalid_format'),
        pytest.param('', "Could not extract date from:", id='empty_string'),
        pytest.param('1.2.2023', "Could not extract date from: 1.2.2023", id='single_digit_day_month'),
    ])
    def test_extract_date_invalid_formats(self, invalid_date, expected_log,
                                         make_raw_entry, run_extractor, caplog):
        """Test date extraction with invalid formats logs warning and date remains None"""
        raw_entries = [make_raw_entry(date=invalid_date)]
        result = run_extractor(raw_entries)

        assert result[0].date is None
        assert expected_log in caplog.text

    def test_extract_date_multiple_entries_different_formats(self, make_raw_entry, run_extractor):
        """Test date extraction with multiple entries in different formats"""
        raw_entries = [
            make_raw_entry(date='15.03.2023', amount='100,00', comment='Test1'),
            make_raw_entry(date='01.06.23', amount='200,00', comment='Test2'),
            make_raw_entry(date='25.12. 25.12.2023', amount='300,00', comment='Test3'),
        ]
        result = run_extractor(raw_entries)

        assert len(result) == 3
        assert result[0].date == datetime.date(2023, 3, 15)
        assert result[1].date == datetime.date(2023, 6, 1)
        assert result[2].date == datetime.date(2023, 12, 25)
