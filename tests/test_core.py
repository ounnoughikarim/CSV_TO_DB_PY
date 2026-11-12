import pytest
from csv_to_db_py import core


def _config(tmp_path):
    return {
        "DATABASE_CONFIG": {
            "type": "postgres",
            "host": "localhost",
            "port": 5432,
            "user": "u",
            "password": "p",
            "database": "db",
        },
        "files_dir": str(tmp_path / "input"),
        "table": "t",
    }


def test_get_connector_raises_on_unsupported_db():
    with pytest.raises(ValueError):
        core.get_connector({"type": "sqlite"})


def test_load_csv_to_db_uses_input_path_over_files_dir(monkeypatch, tmp_path):
    csv_file = tmp_path / "data.csv"
    csv_file.write_text("a,b\n1,2\n")
    cfg = _config(tmp_path)
    cfg["files_dir"] = str(tmp_path / "nonexistent")  # doit être ignoré
    called = {}

    class FakeConnector:
        def __init__(self, dbcfg):
            called["dbcfg"] = dbcfg

        def connect(self):
            pass

        def get_engine(self):
            return None

    monkeypatch.setattr(core, "get_connector", lambda dbcfg: FakeConnector(dbcfg))
    # engine=None -> create_table_from_csv échouera; on teste uniquement l'ordre
    with pytest.raises(Exception):
        core.load_csv_to_db(cfg, input_path=str(csv_file))
    assert called["dbcfg"] == cfg["DATABASE_CONFIG"]


def test_load_csv_to_db_invalid_path_raises(tmp_path):
    cfg = _config(tmp_path)
    with pytest.raises(ValueError):
        core.load_csv_to_db(cfg, input_path="/nonexistent/file.csv")
