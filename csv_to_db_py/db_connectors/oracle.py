from sqlalchemy import URL, create_engine
from csv_to_db_py.db_connectors.base import BaseDBConnector


class OracleConnector(BaseDBConnector):
    def connect(self):
        cfg = self.config
        # DSN Oracle: host:port/service_name (ex: localhost:1521/XEPDB1)
        # SQLAlchemy mappe `database` sur un SID ; il faut passer un service_name
        url = URL.create(
            "oracle+oracledb",
            username=cfg["user"],
            password=cfg["password"],
            host=cfg["host"],
            port=cfg["port"],
            query={"service_name": cfg["database"]},
        )
        self.engine = create_engine(url)
