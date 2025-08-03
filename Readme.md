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

## ToDo
* Tagging of internal transactions. Positive or negative amount. Consider current is_virtual, non_virtual filters for this usecase.
* Remove assumption that input CSV entries are sorted by descending date
* Remove assumption that List[InterpretedEntries] have the order as they were read. Used by EntryAugmentation
* Remove assumption that input CSV files are read in ascending data order. Use by EntryInsights.initial_balance
