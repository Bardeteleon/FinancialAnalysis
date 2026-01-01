import pytest
from statement.extractor.RawEntriesFromCsvExtractor import RawEntriesFromCsvExtractor
from data_types.Config import Config, HeadingConfig, Account
from data_types.RawEntry import RawEntry, RawEntryType
from file_reader.CsvReader import CsvReader

@pytest.fixture
def mock_csv_reader(mocker):
    mock = mocker.MagicMock(spec=CsvReader)
    mock.get_input_file.return_value = 'some/path/some/path/file.csv'
    return mock

@pytest.fixture
def mock_account(mocker):
    account = mocker.MagicMock(spec=Account)
    account.get_input_directory.return_value = 'some/path'
    return account

@pytest.fixture
def mock_config(mocker, mock_account):
    config = mocker.MagicMock(spec=Config)
    config.headings = [
        HeadingConfig(date=['header1'], amount=['header2'], comment=['header3'])
    ]
    config.internal_accounts = [mock_account]
    return config

@pytest.fixture
def run_extractor(mock_csv_reader, mock_config):
    def _run(input_path='some/path'):
        extractor = RawEntriesFromCsvExtractor(mock_csv_reader, mock_config, input_path)
        extractor.run()
        return extractor.get_raw_entries()
    return _run


def test_run_success(mock_csv_reader, run_extractor):
    mock_csv_reader.get_content.return_value = [
        ['header1', 'header2', 'header3', 'header4'],
        ['date1', 'amount1', 'comment1', 'other1'],
        ['date2', 'amount2', 'comment2', 'other2']
    ]

    result = run_extractor()

    assert len(result) == 2
    # Entries now preserved in original CSV order (not reversed)
    assert result[0] == RawEntry(date='date1', amount='amount1', comment='comment1',
                                 account_idx=0, type=RawEntryType.TRANSACTION)
    assert result[1] == RawEntry(date='date2', amount='amount2', comment='comment2',
                                 account_idx=0, type=RawEntryType.TRANSACTION)

@pytest.mark.parametrize("csv_content,headings,accounts", [
    pytest.param(
        [['header1', 'header2']],
        [],
        [],
        id='csv_too_short'
    ),
    pytest.param(
        [['wrong_header1', 'wrong_header2'], ['data1', 'data2']],
        [HeadingConfig(date=['header1'], amount=['header2'], comment=['header3'])],
        [],
        id='no_heading_found'
    ),
    pytest.param(
        [['header1', 'header2', 'header3'], ['data1', 'data2', 'data3']],
        [HeadingConfig(date=['header1'], amount=['header2'], comment=['header3'])],
        [],
        id='no_account_found'
    ),
])
def test_run_error_cases_return_empty(csv_content, headings, accounts,
                                      mock_csv_reader, mock_config, run_extractor):
    mock_csv_reader.get_content.return_value = csv_content
    mock_config.headings = headings
    mock_config.internal_accounts = accounts

    result = run_extractor('')
    assert len(result) == 0

@pytest.mark.parametrize("headers", [
    pytest.param(['header_x', 'header2', 'header3'], id='missing_date'),
    pytest.param(['header1', 'header_x', 'header3'], id='missing_amount'),
    pytest.param(['header1', 'header2', 'header_x'], id='missing_comment'),
])
def test_run_missing_required_column(headers, mock_csv_reader, run_extractor):
    mock_csv_reader.get_content.return_value = [headers, ['data1', 'data2', 'data3']]

    result = run_extractor()
    assert len(result) == 0
