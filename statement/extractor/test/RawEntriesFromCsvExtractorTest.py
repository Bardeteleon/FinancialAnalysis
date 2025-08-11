import pytest
from statement.extractor.RawEntriesFromCsvExtractor import RawEntriesFromCsvExtractor
from data_types.Config import Config, HeadingConfig, Account
from data_types.Types import RawEntry, RawEntryType
from file_reader.CsvReader import CsvReader

@pytest.fixture
def mock_account(mocker):
    account = mocker.MagicMock(spec=Account)
    account.get_input_directory.return_value = 'some/path'
    return account

@pytest.fixture
def mock_csv_reader(mocker):
    mock = mocker.MagicMock(spec=CsvReader)
    mock.get_input_file.return_value = 'some/path/some/path/file.csv'
    return mock

@pytest.fixture
def mock_config(mocker):
    return mocker.MagicMock(spec=Config)

def test_run_success(mock_csv_reader, mock_config, mock_account):
    # Arrange
    mock_csv_reader.get_content.return_value = [
        ['header1', 'header2', 'header3', 'header4'],
        ['date1', 'amount1', 'comment1', 'other1'],
        ['date2', 'amount2', 'comment2', 'other2']
    ]
    mock_config.headings = [
        HeadingConfig(date=['header1'], amount=['header2'], comment=['header3'])
    ]
    mock_config.internal_accounts = [mock_account]

    extractor = RawEntriesFromCsvExtractor(mock_csv_reader, mock_config, 'some/path')

    # Act
    extractor.run()
    result = extractor.get_raw_entries()

    # Assert
    assert len(result) == 2
    assert result[0] == RawEntry(date='date2', amount='amount2', comment='comment2', account_idx=0, type=RawEntryType.TRANSACTION)
    assert result[1] == RawEntry(date='date1', amount='amount1', comment='comment1', account_idx=0, type=RawEntryType.TRANSACTION)

def test_run_csv_too_short(mock_csv_reader, mock_config):
    # Arrange
    mock_csv_reader.get_content.return_value = [['header1', 'header2']]
    extractor = RawEntriesFromCsvExtractor(mock_csv_reader, mock_config, '')

    # Act
    extractor.run()
    result = extractor.get_raw_entries()

    # Assert
    assert len(result) == 0

def test_run_no_heading_found(mock_csv_reader, mock_config):
    # Arrange
    mock_csv_reader.get_content.return_value = [
        ['wrong_header1', 'wrong_header2'],
        ['data1', 'data2']
    ]
    mock_config.headings = [
        HeadingConfig(date=['header1'], amount=['header2'], comment=['header3'])
    ]
    extractor = RawEntriesFromCsvExtractor(mock_csv_reader, mock_config, '')

    # Act
    extractor.run()
    result = extractor.get_raw_entries()

    # Assert
    assert len(result) == 0

def test_run_missing_date_column(mock_csv_reader, mock_config, mock_account):
    # Arrange
    mock_csv_reader.get_content.return_value = [
        ['header_x', 'header2', 'header3'],
        ['data1', 'data2', 'data3']
    ]
    mock_config.headings = [
        HeadingConfig(date=['header1'], amount=['header2'], comment=['header3'])
    ]
    mock_config.internal_accounts = [mock_account]
    extractor = RawEntriesFromCsvExtractor(mock_csv_reader, mock_config, '')

    # Act
    extractor.run()
    result = extractor.get_raw_entries()

    # Assert
    assert len(result) == 0

def test_run_missing_amount_column(mock_csv_reader, mock_config, mock_account):
    # Arrange
    mock_csv_reader.get_content.return_value = [
        ['header1', 'header_x', 'header3'],
        ['data1', 'data2', 'data3']
    ]
    mock_config.headings = [
        HeadingConfig(date=['header1'], amount=['header2'], comment=['header3'])
    ]
    mock_config.internal_accounts = [mock_account]
    extractor = RawEntriesFromCsvExtractor(mock_csv_reader, mock_config, '')

    # Act
    extractor.run()
    result = extractor.get_raw_entries()

    # Assert
    assert len(result) == 0

def test_run_missing_comment_column(mock_csv_reader, mock_config, mock_account):
    # Arrange
    mock_csv_reader.get_content.return_value = [
        ['header1', 'header2', 'header_x'],
        ['data1', 'data2', 'data3']
    ]
    mock_config.headings = [
        HeadingConfig(date=['header1'], amount=['header2'], comment=['header3'])
    ]
    mock_config.internal_accounts = [mock_account]
    extractor = RawEntriesFromCsvExtractor(mock_csv_reader, mock_config, '')

    # Act
    extractor.run()
    result = extractor.get_raw_entries()

    # Assert
    assert len(result) == 0

def test_run_no_account_found(mock_csv_reader, mock_config):
    # Arrange
    mock_csv_reader.get_content.return_value = [
        ['header1', 'header2', 'header3'],
        ['data1', 'data2', 'data3']
    ]
    mock_config.headings = [
        HeadingConfig(date=['header1'], amount=['header2'], comment=['header3'])
    ]
    mock_config.internal_accounts = [] # No accounts in config
    extractor = RawEntriesFromCsvExtractor(mock_csv_reader, mock_config, '')

    # Act
    extractor.run()
    result = extractor.get_raw_entries()

    # Assert
    assert len(result) == 0