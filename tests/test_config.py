import json

import pytest

from csv_to_db_py.config import load_config, validate_config


def test_empty_config_raises():
    with pytest.raises(ValueError):
        validate_config({})


def test_valid_config_does_not_raise():
    validate_config(
        {
            "DATABASE_CONFIG": {
                "type": "postgres",
                "host": "localhost",
                "port": 5432,
                "user": "user",
                "password": "pass",
                "database": "db",
            },
            "files_dir": "x",
        }
    )


def test_unsupported_db_type_raises():
    with pytest.raises(ValueError):
        validate_config({"DATABASE_CONFIG": {"type": "sqlite"}, "files_dir": "x"})


def test_load_config_reads_and_validates(tmp_path):
    cfg = {
        "DATABASE_CONFIG": {
            "type": "postgres",
            "host": "localhost",
            "port": 5432,
            "user": "u",
            "password": "p",
            "database": "db",
        },
        "files_dir": "x",
    }
    path = tmp_path / "config.json"
    path.write_text(json.dumps(cfg))
    assert load_config(str(path)) == cfg


def test_load_config_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_config(str(tmp_path / "missing.json"))
