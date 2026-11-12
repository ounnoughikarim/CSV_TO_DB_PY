import polars as pl
from csv_to_db_py.utils.cleaned_csv import apply_filter


def test_filter_int_column_with_string_value():
    df = pl.DataFrame({"age": pl.Series([18, 25, 18], dtype=pl.Int64)})
    result = apply_filter(df, {"column": "Age", "value": "18"})
    assert result["age"].to_list() == [18, 18]


def test_filter_missing_column_returns_unchanged():
    df = pl.DataFrame({"age": [18, 25]})
    result = apply_filter(df, {"column": "missing", "value": "18"})
    assert result.shape == df.shape
    assert result["age"].to_list() == [18, 25]


def test_filter_non_castable_value_returns_unchanged():
    df = pl.DataFrame({"age": pl.Series([18, 25], dtype=pl.Int64)})
    result = apply_filter(df, {"column": "Age", "value": "abc"})
    assert result.shape == df.shape
    assert result["age"].to_list() == [18, 25]


def test_filter_string_column_filters_normally():
    df = pl.DataFrame({"name": ["alice", "bob"]})
    result = apply_filter(df, {"column": "name", "value": "alice"})
    assert result["name"].to_list() == ["alice"]


def test_filter_empty_config_returns_unchanged():
    df = pl.DataFrame({"age": [18, 25]})
    result = apply_filter(df, {})
    assert result.shape == df.shape
