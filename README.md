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
- MySQL/MSSQL/Oracle connections rely on bundled drivers: `pymysql`, `pyodbc`, `oracledb`
- `pyodbc` additionally requires an ODBC driver; `oracledb` runs in thin mode (no Oracle client needed)



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
    "datetime_detection_threshold": 1.0,
    "batch_size": 100000
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
- `batch_size`: *(optional)* Number of rows to insert per batch for large files
  - Default: `10000` (10k rows per batch)
  - Reduces memory usage for large datasets
  - SQLAlchemy can struggle with very large files, batching prevents memory issues
  - **Recommended values:**
    - `100000`: Good for most cases (files up to several GB)
    - `50000`: For memory-constrained environments
    - `10000`: Default (10k rows per batch), good balance of speed and memory
    - `500000`: For high-memory systems and faster insertions

## Usage

```bash
uv run python -m csv_to_db_py.main
```

With custom log level:
```bash
uv run python -m csv_to_db_py.main --log-level info
```

## Testing

Run the test suite with pytest:
```bash
uv run pytest
```

This suite tests automatic datetime detection with various date formats, using [tests/date_formats_test.csv](tests/date_formats_test.csv) containing 14 columns:

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

### Batch Insertion for Large Files

For large datasets, the tool automatically splits data insertion into batches to prevent memory issues:

**How it works:**
- If total rows ≤ `batch_size`: Single insertion (fastest)
- If total rows > `batch_size`: Multiple insertions in batches

**Example with 250,000 rows and `batch_size: 100000`:**
```
Pre-step: TRUNCATE table if it already exists (preserves schema & dependent views)
Batch 1: Rows 1 to 100,000 (100,000 rows) - APPEND
Batch 2: Rows 100,001 to 200,000 (100,000 rows) - APPEND
Batch 3: Rows 200,001 to 250,000 (50,000 rows) - APPEND
```

**Benefits:**
- ✅ Prevents memory overflow with large files
- ✅ Better progress tracking through logs
- ✅ Allows processing files larger than available RAM
- ✅ Automatic recovery possible (first batch creates table structure)

### Table Overwrite Strategy

When a table already exists, the tool **does not DROP** it. Instead it runs `TRUNCATE` then appends the new data.

**Why:**

- Dropping a table fails if a view (or other object) depends on it.
- TRUNCATE empties the rows while preserving the table schema and any dependent views/constraints.

**Behavior:**

- Table does not exist → pre-created by `create_table_from_csv` with detected types.
- Table exists → `TRUNCATE TABLE "<name>"` then `INSERT` (append mode). If the existing table's columns differ from the CSV (schema drift), the run aborts with a clear error **before truncating**, so the old data is preserved.

**Caveat — schema drift:**

- TRUNCATE keeps the **existing** column definitions. Column-name drift (added/removed/renamed columns) is detected and blocks the overwrite before any data is lost. Type drift is not detected and still fails loudly after truncate.
- To load a CSV whose schema differs, manually `DROP TABLE ... CASCADE` (and recreate dependent views) or alter the table to match the new schema.

**Performance tips:**
- Larger batch sizes = faster insertion but more memory usage
- Smaller batch sizes = slower but safer for limited memory
- Default 10k is optimal for most use cases

### Type Detection Optimization (Sampling)

For large datasets, type detection automatically uses random sampling to improve performance:

**How it works:**
- If DataFrame has ≤ 10,000 rows: Full dataset is analyzed
- If DataFrame has > 10,000 rows: Random sample of 10,000 rows is used
- Sample uses fixed seed (42) for reproducibility
- Applies to both type detection and datetime format detection

**Benefits:**
- ✅ Significantly faster type detection for large files (millions of rows)
- ✅ Sample size of 10,000 rows provides excellent type accuracy
- ✅ Reduces processing time without compromising quality
- ✅ Transparent logging when sampling is used

**Example:**
```
DataFrame contient 5,000,000 lignes. Utilisation d'un échantillon aléatoire de 10000 lignes pour la détection des types.
```

**Note:** This optimization only affects type detection. The full dataset is still loaded and inserted into the database.

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
uv run ruff format
```