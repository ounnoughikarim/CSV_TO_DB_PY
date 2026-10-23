import polars as pl
import pytest

from csv_to_db_py.utils.csv_loader import _truncate_if_exists
from csv_to_db_py.utils.table_creator import create_table_from_csv


class BoomConn:
    def execute(self, sql):
        raise RuntimeError("boom")


class BoomCtx:
    def __init__(self, conn):
        self._conn = conn

    def __enter__(self):
        return self._conn

    def __exit__(self, *exc):
        return False


class StubEngine:
    def __init__(self):
        self._conn = BoomConn()

    def begin(self):
        return BoomCtx(self._conn)


def test_create_table_from_csv_propagates_execute_error(monkeypatch):
    monkeypatch.setattr(
        "csv_to_db_py.utils.table_creator.existing_columns", lambda engine, table: None
    )
    df = pl.DataFrame({"col": [1, 2, 3]})
    with pytest.raises(RuntimeError):
        create_table_from_csv(StubEngine(), df, "t", {"col": "INTEGER"})


def test_truncate_if_exists_propagates_execute_error(monkeypatch):
    monkeypatch.setattr(
        "csv_to_db_py.utils.csv_loader.existing_columns", lambda engine, table: ["col"]
    )
    with pytest.raises(RuntimeError):
        _truncate_if_exists(StubEngine(), "t", ["col"])


def test_truncate_raises_on_schema_drift_without_truncating(monkeypatch):
    monkeypatch.setattr(
        "csv_to_db_py.utils.csv_loader.existing_columns",
        lambda engine, table: ["old_col"],
    )
    with pytest.raises(ValueError, match="Schema drift"):
        _truncate_if_exists(StubEngine(), "t", ["new_col"])


def test_truncate_skips_when_table_missing(monkeypatch):
    monkeypatch.setattr(
        "csv_to_db_py.utils.csv_loader.existing_columns", lambda engine, table: None
    )
    assert _truncate_if_exists(StubEngine(), "t", ["col"]) is False


def test_truncate_executes_when_columns_match(monkeypatch):
    class CountingConn:
        executed = []

        def execute(self, sql):
            CountingConn.executed.append(sql)

    class CountingCtx:
        def __init__(self, conn):
            self._conn = conn

        def __enter__(self):
            return self._conn

        def __exit__(self, *exc):
            return False

    class MatchingEngine:
        def begin(self):
            return CountingCtx(CountingConn())

    monkeypatch.setattr(
        "csv_to_db_py.utils.csv_loader.existing_columns",
        lambda engine, table: ["a", "b"],
    )
    assert _truncate_if_exists(MatchingEngine(), "t", ["a", "b"]) is True
    assert CountingConn.executed and "TRUNCATE" in str(CountingConn.executed[0])
