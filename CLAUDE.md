# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

A Python tool to analyze and visualize bank statements from CSV and PDF files. The system extracts raw entries, interprets them, applies tagging rules, augments data (e.g., for virtual accounts), validates consistency, and provides an interactive Tkinter-based visualization interface.

## System Requirements

- Python 3.9 (specified in Pipfile)
- pipenv for dependency management
- python3-tk for GUI components
- libmagic1 for file type detection

## Development Commands

### Environment Setup
```bash
# Initialize virtual environment (if not exists)
mkdir .venv
pipenv install

# Activate environment
pipenv shell

# Deactivate when done
pipenv exit
```

### Running the Application
```bash
# Main entry point
pipenv run python user_interface/script.py

# The script expects command-line arguments for:
# - input directory path
# - tags JSON configuration path
# - config JSON configuration path
```

### Testing
```bash
# Run all tests
pipenv run pytest

# Run specific test file
pipenv run pytest statement/test/EntryInsightsTest.py

# Run tests in a specific directory
pipenv run pytest statement/extractor/test/
```

Test files follow the pattern `*Test.py` (configured in pytest.ini).

### Building Deployment Binary
```bash
pyinstaller --onefile FinancialAnalysis.py
```

## Architecture

### Core Data Flow

The application follows a pipeline architecture:

1. **Input Reading** (`file_reader/`)
   - `CsvReader`: Reads CSV bank statements
   - `PdfReader`: Extracts text from PDF bank statements using PyPDF2

2. **Raw Extraction** (`statement/extractor/`)
   - `RawEntriesFromCsvExtractor`: Parses CSV content into RawEntry objects in their original order
   - `RawEntriesFromPdfTextExtractor`: Parses PDF text into RawEntry objects
   - Produces `RawEntry` objects with string-based data

3. **Interpretation** (`statement/extractor/InterpretedStatementExtractor`)
   - Converts RawEntry to InterpretedEntry
   - Parses amounts, dates, and identifies card types
   - Applies tag definitions from TagConfig based on comment patterns, date ranges, and account IDs
   - Classifies transactions as internal/external based on IBANs in config
   - Adds UndefinedTag to untagged entries
   - Ensures entries are in ascending date order:
     - Already ascending: no change
     - Descending order: reverses entries
     - Mixed order: stable sort by date (preserves order for same dates)

4. **Augmentation** (`statement/EntryAugmentation`)
   - Replaces alternative IBANs with canonical IBANs (for accounts with multiple identifiers)
   - Creates mirror transactions for virtual accounts (accounts without input files)
   - Adds manual balance entries from config references

5. **Validation** (`statement/EntryValidator`)
   - Validates that transaction amounts match balance progressions

6. **Output**
   - `EntryWriter`: Exports interpreted entries to CSV (exported to `export/` directory)
   - `InteractiveOverviewTkinter`: Launches GUI for visualization
   - `EntryPrinter`: Console output utilities including statistics

### Key Data Types (`data_types/Types.py`)

- **RawEntry**: Unprocessed entry with string fields (date, amount, comment, account_idx, type)
- **InterpretedEntry**: Processed entry with typed fields (date as date object, amount as float, tags, card_type, account_id, type)
  - Has `raw` field linking back to original RawEntry
  - Virtual entries (created by augmentation) have `raw=None`

### Configuration System

Two main configuration files required:

1. **Config JSON** (`data_types/Config.py`)
   - `internal_accounts`: List of Account objects defining known accounts
     - Each Account has: name, transaction_iban, optional transaction_iban_alternative, optional input_directory, optional balance_reference
     - Virtual accounts have `input_directory=None` (no input file, transactions inferred from other accounts)
   - `headings`: CSV column name mappings for date, amount, comment
   - `custom_balances`: Optional custom balance calculations

2. **Tags JSON** (`data_types/TagConfig.py`)
   - `tag_definitions`: Rules for tagging transactions
     - Each TagDefinition has: tag, comment_pattern (regex), optional date_from/date_to, optional account_id
     - Tags matched via regex against transaction comments

### Entry Classification Logic

- **Internal vs External Transactions**:
  - For CREDIT cards: positive amounts are internal, negative are external
  - For GIRO cards: transactions containing internal IBANs in comment are internal, others external

- **Virtual Account Handling**:
  - Accounts marked as virtual (no `input_directory`) have their transactions inferred
  - For each transaction where a virtual account is the counterparty, a mirror transaction is created with negated amount

### Utility Modules

- `statement/EntryFilter`: Filter entries by type, tags, date ranges, account
- `statement/EntrySorter`: Sort entries by date or amount
- `statement/EntryMapping`: Entry transformation utilities
- `statement/EntryInsights`: Calculate statistics and insights
- `user_interface/logger`: Logging configuration
- `user_interface/InputArgumentParser`: CLI argument parsing
- `user_interface/InputArgumentInterpreter`: Converts CLI args to FinancialAnalysisInput

## Important Notes

- **EREF**: Unique transaction identifier (mentioned in README)
- The codebase has known assumptions to be aware of:
  - List[InterpretedEntry] order matters for EntryAugmentation (assumption to be removed)
  - CSV files read order affects EntryInsights.initial_balance (assumption to be removed)
- Main orchestration happens in `FinancialAnalysis.py` class
- Entry point for execution is `user_interface/script.py`
