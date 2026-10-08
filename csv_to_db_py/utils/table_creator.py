from csv_to_db_py.logger import logger
from csv_to_db_py.utils.cleaned_csv import quote_identifier


def create_table_from_csv(engine, dataframe, table, types_dict):
    # Génération de la requête SQL pour créer la table
    # query = f"CREATE TABLE {table} ({', '.join([column + ' '+types_dict[column] for column in columns])});"
    columns = dataframe.columns
    query = f"""CREATE TABLE IF NOT EXISTS {quote_identifier(table)} ({", ".join([quote_identifier(column) + " " + types_dict[column] for column in columns])});"""
    with engine.begin() as conn:
        conn.execute(query)

    logger.info(f"Table '{table}' crée")

    columns = dataframe.columns

    logger.debug(columns)

    logger.debug(query)
