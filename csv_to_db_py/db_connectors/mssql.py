from sqlalchemy import URL, create_engine
from csv_to_db_py.db_connectors.base import BaseDBConnector


class MSSQLConnector(BaseDBConnector):
    def connect(self):
        cfg = self.config
        url = URL.create(
            "mssql+pyodbc",
            username=cfg["user"],
            password=cfg["password"],
            host=cfg["host"],
            port=cfg["port"],
            database=cfg["database"],
            query={"driver": "ODBC Driver 17 for SQL Server"},
        )
        self.engine = create_engine(url)
