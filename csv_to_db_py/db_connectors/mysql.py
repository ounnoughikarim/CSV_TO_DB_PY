from sqlalchemy import URL, create_engine
from csv_to_db_py.db_connectors.base import BaseDBConnector


class MySQLConnector(BaseDBConnector):
    def connect(self):
        cfg = self.config
        url = URL.create(
            "mysql+pymysql",
            username=cfg["user"],
            password=cfg["password"],
            host=cfg["host"],
            port=cfg["port"],
            database=cfg["database"],
        )
        self.engine = create_engine(url)
