# Financial Analysis

A tool to analyse and visualise bank statements. 

## Setup
* install git and clone repository
* install Python 3 and pipenv
* install python3-tk
* install libmagic1
* mkdir .venv
* pipenv install

## Run 
* pipenv shell
* python -m package.file
* pytest directory/
* pipenv exit

## Deployment
pyinstaller --onefile FinancialAnalysis.py

## Help
* EREF: unique transaction identifier 

## Implicits
* List[InterpretedEntries] have the order as they were read. Used by
    * EntryAugmentation

## ToDo
* Warn if some heading config was not found or used
* Define input to accounts by directory rather than input_file_identification
* Rectify account_id. Either from input_file_identification or its transaction_iban.