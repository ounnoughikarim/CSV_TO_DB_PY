from csv_to_db_py.config import config

from utils.table_creator import create_table_from_csv
from db_connectors import postgres, mysql, mssql, oracle
from utils.csv_loader import postgrestype_dict, overwrite_table_with_csv_data
from utils.cleaned_csv import get_dataframe_cleaned
from logger import set_logger

import argparse


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
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-l",
        "--log-level",
        choices=["error", "warning", "info", "debug"],
        default="info",
    )
    args = parser.parse_args()
    logger = set_logger(args.log_level)

    logger.debug(f"DATABASE_CONFIG: {config['DATABASE_CONFIG']}")

    # Connexion DB
    connector = get_connector(config["DATABASE_CONFIG"])
    connector.connect()
    engine = connector.get_engine()

    df = get_dataframe_cleaned(config["file_path"])

    logger.debug(df.columns)

    types_dict = postgrestype_dict(df)
    logger.debug(types_dict)
    create_table_from_csv(engine, df, config["table"], types_dict)
    logger.info("done")
    df.dropna(how="all", inplace=True)
    # desactivate_constraint(i,conn)
    # delete_table_content(i,conn)
    overwrite_table_with_csv_data(engine, df, config["table"])


if __name__ == "__main__":
    main()
