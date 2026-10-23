import polars as pl
from csv_to_db_py.utils.cleaned_csv import quote_identifier
from csv_to_db_py.utils.table_creator import create_table_from_csv


def test_quote_identifier_escapes_embedded_quote():
    assert quote_identifier('my"data') == '"my""data"'


def test_quote_identifier_quotes_reserved_word():
    assert quote_identifier("order") == '"order"'


def test_quote_identifier_quotes_normal_name():
    assert quote_identifier("normal") == '"normal"'


def test_quote_identifier_uses_backticks_for_mysql():
    assert quote_identifier("my`data", "mysql") == "`my``data`"
    assert quote_identifier("order", "mysql") == "`order`"


def test_create_table_from_csv_quotes_table_and_columns(monkeypatch):
    class StubConn:
        def __init__(self):
            self.statements = []

        def execute(self, sql):
            self.statements.append(sql)

    class StubBegin:
        def __init__(self, conn):
            self.conn = conn

        def __enter__(self):
            return self.conn

        def __exit__(self, *args):
            return False

    class StubEngine:
        def __init__(self):
            self.conn = StubConn()

        def begin(self):
            return StubBegin(self.conn)

    monkeypatch.setattr(
        "csv_to_db_py.utils.table_creator.existing_columns", lambda engine, table: None
    )

    df = pl.DataFrame({"col": [1, 2]})
    engine = StubEngine()
    create_table_from_csv(engine, df, "order", {"col": "INTEGER"})
    recorded = str(engine.conn.statements[0])
    assert '"order"' in recorded
    assert '"col"' in recorded


def test_create_table_from_csv_skips_when_table_exists(monkeypatch):
    class StubEngine:
        def begin(self):
            raise AssertionError("must not execute CREATE when table exists")

    monkeypatch.setattr(
        "csv_to_db_py.utils.table_creator.existing_columns",
        lambda engine, table: ["col"],
    )

    df = pl.DataFrame({"col": [1, 2]})
    create_table_from_csv(StubEngine(), df, "order", {"col": "INTEGER"})
