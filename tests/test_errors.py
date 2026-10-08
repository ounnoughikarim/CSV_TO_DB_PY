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


def test_create_table_from_csv_propagates_execute_error():
    df = pl.DataFrame({"col": [1, 2, 3]})
    with pytest.raises(RuntimeError):
        create_table_from_csv(StubEngine(), df, "t", {"col": "INTEGER"})


def test_truncate_if_exists_propagates_execute_error(monkeypatch):
    class FakeInspector:
        def has_table(self, name):
            return True

    monkeypatch.setattr(
        "csv_to_db_py.utils.csv_loader.inspect", lambda engine: FakeInspector()
    )
    with pytest.raises(RuntimeError):
        _truncate_if_exists(StubEngine(), "t")
