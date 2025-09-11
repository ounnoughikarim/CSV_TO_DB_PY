from sqlalchemy.dialects.postgresql import VARCHAR, INTEGER, FLOAT, BOOLEAN, DATE, TIMESTAMP
import psycopg2
import pandas as pd
import re
from collections import Counter
from csv_to_db_py.config import config

from utils.table_creator import create_table_from_csv
from db_connectors import postgres, mysql, mssql, oracle
from utils.csv_loader import pandas_type_to_sql, map_pandas_dtype_to_postgresql, postgrestype_dict, overwrite_table_with_csv_data
from utils.cleaned_csv import normalize_column, get_dataframe_cleaned, normalize_column, normalize_and_dedup_columns


import re

import json
import logging
from sqlalchemy import text, create_engine, inspect
from datetime import datetime
import os 
from openpyxl.utils import get_column_letter
from openpyxl.chart import LineChart, Reference, Series
from datetime import datetime






logging.basicConfig(level=logging.INFO)




 
    




# ---------------------------------------------------------------------------
# Utilitaires
# ---------------------------------------------------------------------------


def get_connector(config):
    db_type = config['type']
    if db_type == 'postgres':
        return postgres.PostgresConnector(config)
    elif db_type == 'mysql':
        return mysql.MySQLConnector(config)
    elif db_type == 'mssql':
        return mssql.MSSQLConnector(config)
    elif db_type == 'oracle':
        return oracle.OracleConnector(config)
    else:
        raise ValueError("Base de données non supportée")


def main() -> None:


    
    
   
    print(config['DATABASE_CONFIG'])
    # Connexion DB
    connector = get_connector(config['DATABASE_CONFIG'])
    connector.connect()
    engine = connector.get_engine()  

    df=get_dataframe_cleaned(config['file_path'])

    print(df.columns)

    types_dict=postgrestype_dict(df)
    print(types_dict)
    create_table_from_csv(engine,df,config['table'],types_dict)
    print ('done')
    df.dropna(how='all',inplace=True)
    #desactivate_constraint(i,conn)
    #delete_table_content(i,conn)
    overwrite_table_with_csv_data(engine, df, config['table'])




if __name__ == "__main__":

    main()

