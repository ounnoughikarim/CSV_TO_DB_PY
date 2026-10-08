import pytest
from sqlalchemy.engine import make_url

from csv_to_db_py.db_connectors.mssql import MSSQLConnector
from csv_to_db_py.db_connectors.mysql import MySQLConnector
from csv_to_db_py.db_connectors.oracle import OracleConnector
from csv_to_db_py.db_connectors.postgres import PostgresConnector


def _config():
    return {
        "user": "user",
        "password": "p@ss:w/rd",
        "host": "localhost",
        "port": 5432,
        "database": "db",
    }


@pytest.mark.parametrize(
    "connector_cls,expected_drivername",
    [
        (PostgresConnector, "postgresql+psycopg2"),
        (MySQLConnector, "mysql+pymysql"),
        (OracleConnector, "oracle+cx_oracle"),
        (MSSQLConnector, "mssql+pyodbc"),
    ],
)
def test_connector_url_preserves_password_and_drivername(
    connector_cls, expected_drivername
):
    connector = connector_cls(_config())
    connector.connect()
    url = make_url(connector.engine.url)
    assert url.password == "p@ss:w/rd"
    assert url.drivername == expected_drivername
