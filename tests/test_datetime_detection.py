import polars as pl
import pytest
from pathlib import Path

from csv_to_db_py.utils.csv_loader import detect_and_parse_datetime_column

TEST_FILE = Path(__file__).parent / "date_formats_test.csv"

DATETIME_COLUMNS = [
    "FR_date",
    "FR_datetime",
    "ISO_date",
    "ISO_datetime",
    "USA_date",
    "USA_datetime",
    "EUR_date",
    "EUR_datetime",
    "ISO_time",
]

NON_DATETIME_COLUMNS = [
    "int_column",
    "string_column",
    "mixed_column",
    "float_column",
    "bool_column",
]


@pytest.fixture
def dataframe():
    return pl.read_csv(TEST_FILE)


def _final_dtype(dataframe, column_name):
    return detect_and_parse_datetime_column(dataframe, column_name, threshold=0.7)[
        column_name
    ].dtype


@pytest.mark.parametrize("column_name", DATETIME_COLUMNS)
def test_datetime_column_detected(dataframe, column_name):
    assert _final_dtype(dataframe, column_name) == pl.Datetime


@pytest.mark.parametrize("column_name", NON_DATETIME_COLUMNS)
def test_non_datetime_column_not_detected(dataframe, column_name):
    assert _final_dtype(dataframe, column_name) == dataframe[column_name].dtype
