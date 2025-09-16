from sqlalchemy import create_engine
from db_connectors.base import BaseDBConnector


class MSSQLConnector(BaseDBConnector):
    def connect(self):
        cfg = self.config
        # Exemple : "ODBC Driver 17 for SQL Server" (à adapter si besoin)
        driver = "ODBC Driver 17 for SQL Server"
        url = (
            f"mssql+pyodbc://{cfg['user']}:{cfg['password']}@{cfg['host']}:{cfg['port']}/{cfg['database']}"
            f"?driver={driver.replace(' ', '+')}"
        )
        self.engine = create_engine(url)
