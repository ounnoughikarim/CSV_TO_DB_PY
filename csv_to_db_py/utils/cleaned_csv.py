from collections import Counter
import pandas as pd
import logging
from datetime import datetime
from sqlalchemy import text
import re
from csv_to_db_py.config import config
from csv_to_db_py.config import PG_RESERVED



def normalize_column(name: str) -> str:
    name = name.strip().lower()                # lowercase + trim
    name = re.sub(r'[^0-9a-zA-Z_]+', '_', name) # replace non-alphanum with "_"
    name = re.sub(r'_+', '_', name)             # collapse multiple "_"
    #name = re.sub(r'order', 'xxorder', name)  
    return name.strip('_')    

def get_dataframe_cleaned(file_path) :
    # Lecture des noms de colonnes à partir du fichier
    csv_file=pd.read_csv(file_path,delimiter=config['delimiter'], encoding='utf-8',low_memory=False)
    #csv_file=pd.read_csv(file_path,delimiter=',', encoding='utf-8')
    #csv_file=pd.read_csv(file_path,delimiter='\t', encoding='utf-8')
    #csv_file=pd.read_csv(file_path)
    csv_file.columns=csv_file.columns.str.replace(" ", "")
    csv_file.columns=csv_file.columns.str.replace(".", "")
    csv_file.columns=csv_file.columns.str.replace("/", "")

    # csv_file.columns = [normalize_column(col) for col in csv_file.columns]

    csv_file.columns = normalize_and_dedup_columns(csv_file.columns)

    print(csv_file)
    return csv_file 




def normalize_and_dedup_columns(columns):
    seen = Counter()
    new_cols = []
    for col in columns:
        normed = normalize_column(col)   # ta fonction de normalisation
        seen[normed] += 1
        if seen[normed] == 1:
            new_cols.append(normed)
        else:
            new_cols.append(f"{normed}_{seen[normed]}")
    return new_cols

def normalize_column(name: str) -> str:
    reserved_word = Counter()
    name = name.strip().lower()                  # lowercase + trim
    name = re.sub(r'[^0-9a-zA-Z_]+', '_', name)  # replace non-alphanum with "_"
    name = re.sub(r'_+', '_', name)              # collapse multiple "_"
    name = name.strip('_')                       # remove leading/trailing "_"

    # si le nom est un mot réservé SQL → ajouter suffixe incrémental
    if name in PG_RESERVED:
        reserved_word[name] += 1
        name = f"{name}_{reserved_word[name]}"

    return name