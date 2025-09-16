import pandas as pd
import psycopg2
from logger import logger


def pandas_type_to_sql(dtype):
    if dtype.name.startswith("int"):
        return "INTEGER"
    if dtype.name.startswith("float"):
        return "FLOAT"
    if dtype.name.startswith("bool"):
        return "BOOLEAN"
    if "datetime" in dtype.name:
        return "TIMESTAMP"
    return "TEXT"


def map_pandas_dtype_to_postgresql(series):
    if pd.api.types.is_integer_dtype(series):
        return "INTEGER"
    elif pd.api.types.is_float_dtype(series):
        if series.dropna().apply(lambda x: x.is_integer()).all():
            return "INTEGER"
        else:
            return "FLOAT"
    elif pd.api.types.is_bool_dtype(series):
        return "BOOLEAN"
    elif pd.api.types.is_datetime64_any_dtype(series):
        return "TIMESTAMP"
    elif pd.api.types.is_object_dtype(series):
        return "VARCHAR"
    else:
        return "VARCHAR"


def postgrestype_dict(dataframe):
    # Lecture des noms de colonnes à partir du fichier
    column_types = {}

    for column_name in dataframe.columns:
        if not dataframe[column_name].dtype:
            logger.debug(dataframe[column_name])
        column_dtype = dataframe[column_name].dtype
        if pd.api.types.is_object_dtype(column_dtype):
            try:
                dataframe[column_name] = pd.to_datetime(dataframe[column_name])
                column_dtype = dataframe[column_name].dtype
            except (ValueError, TypeError):
                pass

        column_types[column_name] = map_pandas_dtype_to_postgresql(
            dataframe[column_name]
        )
    return column_types


def overwrite_table_with_csv_data(engine, csv_data, table_name):
    try:
        csv_data.to_sql(name=table_name, con=engine, if_exists="replace", index=False)
        logger.warning(
            f"La table '{table_name}' a été écrasée avec les données du fichier CSV correspondant."
        )
    except psycopg2.Error as e:
        logger.error(
            f"Erreur lors de l'écriture des données dans la table '{table_name}': {e}"
        )
