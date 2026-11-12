from sqlalchemy import text

from csv_to_db_py.logger import logger
from csv_to_db_py.utils.cleaned_csv import (
    dialect_name,
    existing_columns,
    quote_identifier,
)


def create_table_from_csv(engine, dataframe, table, types_dict):
    if existing_columns(engine, table) is not None:
        return

    dialect = dialect_name(engine)
    quote = lambda name: quote_identifier(name, dialect)  # noqa: E731
    columns = dataframe.columns
    query = (
        f"CREATE TABLE {quote(table)} "
        f"({', '.join(quote(column) + ' ' + types_dict[column] for column in columns)})"
    )
    with engine.begin() as conn:
        conn.execute(text(query))

    logger.info(f"Table '{table}' crée")

    logger.debug(columns)
    logger.debug(query)
