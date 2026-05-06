from sqlalchemy import URL, create_engine
from db_connectors.base import BaseDBConnector


class PostgresConnector(BaseDBConnector):
    def connect(self):
        cfg = self.config
        # url = f"postgresql+psycopg2://{cfg['user']}:{cfg['password']}@{cfg['host']}:{cfg['port']}/{cfg['database']}"
        url = URL.create(
            "postgresql+psycopg2",
            username=cfg["user"],
            password=cfg["password"],
            host=cfg["host"],
            port=cfg["port"],
            database=cfg["database"],
        )
        self.engine = create_engine(url)
