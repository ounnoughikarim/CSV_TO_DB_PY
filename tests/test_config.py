import pytest

from csv_to_db_py.config import validate_config


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
