from sqlalchemy import create_engine
from db_connectors.base import BaseDBConnector

class OracleConnector(BaseDBConnector):
    def connect(self):
        cfg = self.config
        # DSN Oracle : host:port/service_name (ex: localhost:1521/XEPDB1)
        dsn = f"{cfg['host']}:{cfg['port']}/{cfg['database']}"
        url = f"oracle+cx_oracle://{cfg['user']}:{cfg['password']}@{dsn}"
        self.engine = create_engine(url)
