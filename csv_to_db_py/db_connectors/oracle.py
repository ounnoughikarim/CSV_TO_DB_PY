from sqlalchemy import URL, create_engine
from csv_to_db_py.db_connectors.base import BaseDBConnector


class OracleConnector(BaseDBConnector):
    def connect(self):
        cfg = self.config
        # DSN Oracle: host:port/service_name (ex: localhost:1521/XEPDB1)
        url = URL.create(
            "oracle+cx_oracle",
            username=cfg["user"],
            password=cfg["password"],
            host=cfg["host"],
            port=cfg["port"],
            database=cfg["database"],
        )
        self.engine = create_engine(url)
