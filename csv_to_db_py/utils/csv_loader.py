import polars as pl
import psycopg2
from logger import logger


def polars_type_to_sql(dtype):
    dtype_str = str(dtype)
    if "Int" in dtype_str:
        return "INTEGER"
    if "Float" in dtype_str:
        return "FLOAT"
    if "Boolean" in dtype_str or "Bool" in dtype_str:
        return "BOOLEAN"
    if "Datetime" in dtype_str or "Date" in dtype_str:
        return "TIMESTAMP"
    return "TEXT"


def map_polars_dtype_to_postgresql(series):
    dtype = series.dtype
    dtype_str = str(dtype)

    if "Int" in dtype_str:
        return "INTEGER"
    elif "Float" in dtype_str:
        # Check if all non-null values are integers
        non_null = series.drop_nulls()
        if len(non_null) > 0 and (non_null == non_null.cast(pl.Int64)).all():
            return "INTEGER"
        else:
            return "FLOAT"
    elif "Boolean" in dtype_str or "Bool" in dtype_str:
        return "BOOLEAN"
    elif "Datetime" in dtype_str or "Date" in dtype_str:
        return "TIMESTAMP"
    elif "Utf8" in dtype_str or "String" in dtype_str:
        return "VARCHAR"
    else:
        return "VARCHAR"


def postgrestype_dict(dataframe):
    # Lecture des noms de colonnes à partir du fichier
    column_types = {}

    for column_name in dataframe.columns:
        column = dataframe[column_name]
        dtype_str = str(column.dtype)

        # Try to parse as datetime if it's a string column
        if "Utf8" in dtype_str or "String" in dtype_str:
            try:
                dataframe = dataframe.with_columns(
                    pl.col(column_name).str.strptime(pl.Datetime, format="%Y-%m-%d %H:%M:%S", strict=False)
                )
            except:
                pass

        column_types[column_name] = map_polars_dtype_to_postgresql(
            dataframe[column_name]
        )
    return column_types


def overwrite_table_with_csv_data(engine, csv_data, table_name):
    try:
        # Convert polars DataFrame to pandas for SQLAlchemy compatibility
        pandas_data = csv_data.to_pandas()
        pandas_data.to_sql(name=table_name, con=engine, if_exists="replace", index=False)
        logger.warning(
            f"La table '{table_name}' a été écrasée avec les données du fichier CSV correspondant."
        )
    except psycopg2.Error as e:
        logger.error(
            f"Erreur lors de l'écriture des données dans la table '{table_name}': {e}"
        )
