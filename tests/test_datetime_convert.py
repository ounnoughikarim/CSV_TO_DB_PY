import polars as pl

from csv_to_db_py.utils.csv_loader import (
    convert_datetime_columns,
    postgrestype_dict,
)


def _dates_df():
    return pl.DataFrame(
        {"dates": ["2024-01-01", "2024-01-02", "2024-01-03", "invalide"]}
    )


def test_convert_datetime_columns_converts_full_dataframe():
    df = convert_datetime_columns(_dates_df(), threshold=0.7)

    assert df["dates"].dtype == pl.Datetime
    assert df["dates"].to_list()[3] is None
    assert postgrestype_dict(df)["dates"] == "TIMESTAMP"


def test_default_threshold_keeps_invalid_column_as_string():
    df = convert_datetime_columns(_dates_df())

    assert df["dates"].dtype == pl.String
    assert df["dates"].to_list() == [
        "2024-01-01",
        "2024-01-02",
        "2024-01-03",
        "invalide",
    ]
