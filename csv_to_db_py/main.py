from csv_to_db_py.config import config

from csv_to_db_py.utils.table_creator import create_table_from_csv
from db_connectors import postgres, mysql, mssql, oracle
from csv_to_db_py.utils.csv_loader import (
    postgrestype_dict,
    overwrite_table_with_csv_data,
)
from utils.cleaned_csv import get_dataframe_cleaned_new
from utils.cleaned_csv import normalize_column

import polars as pl
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
        input_path = config["files_dir"]

    connector = get_connector(config["DATABASE_CONFIG"])
    connector.connect()
    engine = connector.get_engine()

    # Détection du(s) fichier(s) CSV ou XLSX
    if os.path.isfile(input_path) and (
        input_path.endswith(".csv") or input_path.endswith(".xlsx")
    ):
        files = [input_path]

    elif os.path.isdir(input_path):
        files = [
            os.path.join(input_path, f)
            for f in os.listdir(input_path)
            if f.endswith(".csv") or f.endswith(".xlsx")
        ]

    else:
        raise ValueError(
            "Le chemin fourni n'est ni un fichier CSV/XLSX existant ni un dossier valide"
        )

    print(f"Fichiers trouvés : {files}")
    isUniqueFile = len(files) == 1
    for file_path in files:
        print(f"Traitement du fichier : {file_path}")
        df = get_dataframe_cleaned_new(file_path)

        # Appliquer le filtre sur la colonne pour la valeur souhaitée

        filter_config = config.get("FILTER", {})
        filter_col = filter_config.get("column")
        filter_val = filter_config.get("value")

        if filter_col and filter_val:
            normalized_col = normalize_column(filter_col)
            if normalized_col in df.columns:
                df = df.filter(df[normalized_col] == filter_val)
                logging.info(
                    f"Filtre appliqué : {filter_col} = {filter_val} ({len(df)} lignes restantes)"
                )
            else:
                logging.warning(
                    f"Filtre ignoré : colonne '{filter_col}' absente après normalisation."
                )

        print(df.columns)
        types_dict = postgrestype_dict(df)
        print(types_dict)
        
        if isUniqueFile:
            table_name = config['table']
        else:
            table_name = os.path.splitext(os.path.basename(file_path))[0]
        create_table_from_csv(engine, df, table_name, types_dict)
        print(f"Table {table_name} créée")
        # Drop rows where all values are null (polars equivalent)
        df = df.filter(~pl.all_horizontal(pl.all().is_null()))
        overwrite_table_with_csv_data(engine, df, table_name)
        print(f"Données du fichier {file_path} chargées dans la table {table_name}")


if __name__ == "__main__":
    input_arg = sys.argv[1] if len(sys.argv) > 1 else None
    main(input_arg)
