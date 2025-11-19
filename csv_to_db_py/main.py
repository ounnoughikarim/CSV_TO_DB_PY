from csv_to_db_py.config import config

from utils.table_creator import create_table_from_csv
from db_connectors import postgres, mysql, mssql, oracle
from utils.csv_loader import postgrestype_dict, overwrite_table_with_csv_data
from utils.cleaned_csv import get_dataframe_cleaned

import sys
import os
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


def main(input_path=None) -> None:
    if input_path is None:
        input_path = config["csv_dir"]

    connector = get_connector(config["DATABASE_CONFIG"])
    connector.connect()
    engine = connector.get_engine()

    # Détection du(s) fichier(s)
    if os.path.isfile(input_path) and input_path.endswith('.csv'):
        files = [input_path]
    elif os.path.isdir(input_path):
        files = [os.path.join(input_path, f) for f in os.listdir(input_path) if f.endswith('.csv')]
    else:
        raise ValueError("Le chemin fourni n'est ni un fichier CSV existant ni un dossier valide")

    print(f"Fichiers trouvés : {files}")

    for file_path in files:
        print(f"Traitement du fichier : {file_path}")
        df = get_dataframe_cleaned(file_path)
        print(df.columns)
        types_dict = postgrestype_dict(df)
        print(types_dict)

        table_name = f"{config.get('TABLE_PREFIX', '')}{os.path.splitext(os.path.basename(file_path))[0]}"
        create_table_from_csv(engine, df, table_name, types_dict)
        print(f"Table {table_name} créée")
        df.dropna(how="all", inplace=True)
        overwrite_table_with_csv_data(engine, df, table_name)
        print(f"Données du fichier {file_path} chargées dans la table {table_name}")


if __name__ == "__main__":
    input_arg = sys.argv[1] if len(sys.argv) > 1 else None
    main(input_arg)