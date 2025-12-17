# CSV to DB

Convert table files or folders to PostgreSQL database tables.The database need to already exists. It have a feature of autodection of types.
 -dates (multiples formats cited on tests parts)
 -int
 -float
 -string 
 

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
    "delimiter": ";",
    "datetime_detection_threshold": 1.0
}
```

### Configuration Parameters

- `DATABASE_CONFIG`: Database connection settings
  - `type`: Database type (postgres, mysql, mssql, oracle)
  - `host`: Database hostname
  - `port`: Database port
  - `user`: Database username
  - `password`: Database password
  - `database`: Database name
- `files_dir`: Path to a file or folder containing multiple files (CSV or XLSX)
- `table`: Table name (optional - uses filename if not specified for single file)
- `delimiter`: CSV delimiter character (e.g., ";", ",", "\t")
- `datetime_detection_threshold`: *(optional)* Threshold for automatic datetime detection
  - Range: `0.0` to `1.0` (0% to 100%)
  - Default: `1.0` (100%, strict - only perfect matches)
  - Recommended: `0.7` (70% threshold for flexible detection)
  - A column is detected as datetime if at least X% of non-null, non-empty values can be parsed as valid dates
  - Invalid values are automatically converted to NULL
  - **Examples:**
    - `1.0`: Only columns with 100% valid dates are detected (safest, default)
    - `0.9`: Allows up to 10% invalid date values
    - `0.7`: Allows up to 30% invalid date values (recommended for real-world data)

## Usage

```bash
uv run python csv_to_db_py/main.py
```

With custom log level:
```bash
uv run python csv_to_db_py/main.py --log-level info
```

## Testing

Test automatic datetime detection with various date formats:
```bash
uv run python tests/test_datetime_detection.py
```

This test uses a sample CSV file ([tests/date_formats_test.csv](tests/date_formats_test.csv)) containing 14 columns:

**Date columns (should be detected as datetime):**
- **FR_date**: French format (DD/MM/YYYY)
- **FR_datetime**: French format with time (DD/MM/YYYY HH:MM:SS)
- **ISO_date**: ISO 8601 date (YYYY-MM-DD)
- **ISO_datetime**: ISO 8601 with time (YYYY-MM-DDTHH:MM:SS)
- **USA_date**: American format (MM/DD/YYYY)
- **USA_datetime**: American format with 12-hour time (MM/DD/YYYY hh:mm:ss AM/PM)
- **EUR_date**: European format (DD.MM.YYYY)
- **EUR_datetime**: European format with time (DD.MM.YYYY HH:MM:SS)
- **ISO_time**: ISO format with space separator (YYYY-MM-DD HH:MM:SS)

**Non-date columns (should NOT be detected as datetime):**
- **int_column**: Integer values
- **string_column**: Pure text strings
- **mixed_column**: Mix of text with 1-2 dates (should not be detected as datetime)
- **float_column**: Floating point numbers
- **bool_column**: Boolean values

The test demonstrates automatic format detection, handling of null values, conversion of invalid values to null, and proper rejection of non-date columns.

### Datetime Detection Behavior

The datetime detection threshold controls how strict the algorithm is when detecting date columns:

**With `datetime_detection_threshold: 1.0` (default, 100%):**
- Only columns where **ALL** non-null, non-empty values are valid dates will be detected
- This is the safest option to avoid false positives
- Use this when you want explicit control over which columns are dates

**With `datetime_detection_threshold: 0.7` (recommended for flexible detection):**
- Columns where **at least 70%** of non-null, non-empty values are valid dates will be detected
- Invalid values are automatically converted to NULL
- Useful when your data might contain occasional typos or invalid date entries
- Example: A column with 9 valid dates and 1 "invalid" string → detected as datetime

**Example scenarios:**
```
Column: ["2024-01-01", "2024-01-02", "invalid", null, ""]
- 3 non-null, non-empty values total
- 2 valid dates (66.7%)
- With threshold 1.0: NOT detected (66.7% < 100%)
- With threshold 0.7: NOT detected (66.7% < 70%)

Column: ["2024-01-01", "2024-01-02", "2024-01-03", "invalid", null]
- 4 non-null, non-empty values total
- 3 valid dates (75%)
- With threshold 1.0: NOT detected (75% < 100%)
- With threshold 0.7: DETECTED (75% ≥ 70%), "invalid" becomes NULL
```

## Development

Check code before committing:
```bash
uv run ruff check . --fix
uv run ruff check .
```