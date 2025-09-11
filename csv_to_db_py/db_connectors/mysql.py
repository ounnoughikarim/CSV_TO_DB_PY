from sqlalchemy import create_engine
from db_connectors.base import BaseDBConnector

class MySQLConnector(BaseDBConnector):

    def connect(self):
        cfg = self.config
        url = f"mysql+pymysql://{cfg['user']}:{cfg['password']}@{cfg['host']}:{cfg['port']}/{cfg['database']}"
        self.engine = create_engine(url)
