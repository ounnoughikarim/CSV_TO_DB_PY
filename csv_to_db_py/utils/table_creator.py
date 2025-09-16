import logging
# ... autres imports ...


def create_table_from_csv(engine, dataframe, table, types_dict):
    # Génération de la requête SQL pour créer la table
    # query = f"CREATE TABLE {table} ({', '.join([column + ' '+types_dict[column] for column in columns])});"
    columns = dataframe.columns
    query = f"""CREATE TABLE IF NOT EXISTS {table} ({", ".join([column + " " + types_dict[column] for column in columns])});"""
    try:
        with engine.begin() as conn:
            conn.execute(query)

        logging.info(f"Table '{table}' crée")

    except Exception as e:
        print(f"Erreur lors du traitement de '{table}' : {e}")

    columns = dataframe.columns

    print(columns)

    print(query)
