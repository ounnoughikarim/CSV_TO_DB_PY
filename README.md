# Project 

Convert CSV file or folder of CSV to DB with table filled with the CSV data. For now, you can only do it for PostGres databases. 

# Prerequisites

- Download Python 
- Download Poetry (https://python-poetry.org/docs/#installing-with-the-official-installer)
- Download git bash
## Installation

Clone the project 
```
git clone https://github.com/ounnoughikarim/CSV_TO_DB_PY.git
```
Install dependecies with poetry

```
poetry install
```
Create a mainConfig.json file and provide the required information. You can use the mainConfig.json.template file as a reference to know what needs to be filled in.


Run the main script
```
poetry run python csv_to_db_py/main.py
```

you can run it without poetry by installing all dependances with pip then run :
```
python ./csv_to_db_py/main.py
```

Change the logging level with the `--log-level` (or `-l`) option:

```
poetry run python csv_to_db_py/main.py --log-level info
```

