# CSV to DB

Convert table files or folders to PostgreSQL database tables.The database need to already exists.

## Prerequisites

- Python 3.13+
- UV (https://docs.astral.sh/uv/getting-started/installation/)
- PostgreSQL database
- files with CSV or XLSX format



## Installation

```bash
git clone https://github.com/ounnoughikarim/CSV_TO_DB_PY.git
cd CSV_TO_DB_PY
uv sync
```

## Configuration

Create `mainConfig.json` from the template:

```json
{
    "DATABASE_CONFIG": {
        "type": "postgres",
        "host": "hostname",
        "port": 5432,
        "user": "postgres",
        "password": "your_password",
        "database": "your_database"
    },
    "files_dir": "C:\\path\\to\\your\\file",
    "table": "table_name",
    "delimiter": ";"
}
```

- `files_dir`: Path to a  file or folder containing multiple files
- `table`: Table name (optional - uses filename if not specified)
- `delimiter`: CSV delimiter character if the format is CSV

## Usage

```bash
uv run python csv_to_db_py/main.py
```

With custom log level:
```bash
uv run python csv_to_db_py/main.py --log-level info
```

## Development

Check code before committing:
```bash
uv run ruff check . --fix
uv run ruff check .
```