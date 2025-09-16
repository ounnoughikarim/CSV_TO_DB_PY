from csv_to_db_py.config import config

from utils.table_creator import create_table_from_csv
from db_connectors import postgres, mysql, mssql, oracle
from utils.csv_loader import postgrestype_dict, overwrite_table_with_csv_data
from utils.cleaned_csv import get_dataframe_cleaned


import logging


logging.basicConfig(level=logging.INFO)


# ---------------------------------------------------------------------------
# Utilitaires
# ---------------------------------------------------------------------------


def get_connector(config):
    db_type = config["type"]
    if db_type == "postgres":
        return postgres.PostgresConnector(config)
    elif db_type == "mysql":
        return mysql.MySQLConnector(config)
    elif db_type == "mssql":
        return mssql.MSSQLConnector(config)
    elif db_type == "oracle":
        return oracle.OracleConnector(config)
    else:
        raise ValueError("Base de données non supportée")


def main() -> None:
    print(config["DATABASE_CONFIG"])
    # Connexion DB
    connector = get_connector(config["DATABASE_CONFIG"])
    connector.connect()
    engine = connector.get_engine()

    df = get_dataframe_cleaned(config["file_path"])

    print(df.columns)

    types_dict = postgrestype_dict(df)
    print(types_dict)
    create_table_from_csv(engine, df, config["table"], types_dict)
    print("done")
    df.dropna(how="all", inplace=True)
    # desactivate_constraint(i,conn)
    # delete_table_content(i,conn)
    overwrite_table_with_csv_data(engine, df, config["table"])


if __name__ == "__main__":
    main()
