from collections import Counter
import pandas as pd
import re
from csv_to_db_py.config import config
from csv_to_db_py.config import PG_RESERVED

import csv

def detect_delimiter(file_path):
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        sample = f.read(2048)
        try:
            delimiter = csv.Sniffer().sniff(sample).delimiter
        except Exception:
            delimiter = ";"    # fallback si détection impossible : tu peux mettre "," si tu préfères
    return delimiter

def normalize_column(name: str) -> str:
    name = name.strip().lower()  # lowercase + trim
    name = re.sub(r"[^0-9a-zA-Z_]+", "_", name)  # replace non-alphanum with "_"
    name = re.sub(r"_+", "_", name)  # collapse multiple "_"
    # name = re.sub(r'order', 'xxorder', name)
    return name.strip("_")


def get_dataframe_cleaned(file_path):

    # Utiliser le délimiteur du config si dispo, sinon détecter
    delimiter = config.get("delimiter", detect_delimiter(file_path))
    print(f"Délimiteur utilisé pour {file_path}: '{delimiter}'")

    # Essayer UTF-8, sinon fallback Latin-1
    try:
        csv_file = pd.read_csv(file_path, delimiter=delimiter, encoding="utf-8", low_memory=False)
    except UnicodeDecodeError:
        print("[ENCODING] UTF-8 échoué, tentative avec Latin-1...")
        csv_file = pd.read_csv(file_path, delimiter=delimiter, encoding="latin1", low_memory=False)


    # Nettoyage des noms de colonnes
    csv_file.columns = csv_file.columns.str.replace(" ", "")
    csv_file.columns = csv_file.columns.str.replace(".", "")
    csv_file.columns = csv_file.columns.str.replace("/", "")
    csv_file.columns = normalize_and_dedup_columns(csv_file.columns)


    print(csv_file)
    return csv_file


def get_dataframe_cleaned_new(file_path):

    # --- 1) Lecture du fichier selon l'extension ---
    if file_path.endswith(".xlsx"):
        print(f"Lecture Excel : {file_path}")
        df = pd.read_excel(file_path)

    elif file_path.endswith(".csv"):
        print(f"Lecture CSV : {file_path}")

        # Utiliser le délimiteur du config si dispo, sinon détecter
        delimiter = config.get("delimiter", detect_delimiter(file_path))
        print(f"Délimiteur utilisé pour {file_path}: '{delimiter}'")

        # Essayer UTF-8, sinon fallback Latin-1
        try:
            df = pd.read_csv(file_path, delimiter=delimiter, encoding="utf-8", low_memory=False)
        except UnicodeDecodeError:
            print("[ENCODING] UTF-8 échoué, tentative avec Latin-1...")
            df = pd.read_csv(file_path, delimiter=delimiter, encoding="latin1", low_memory=False)

    else:
        raise ValueError(f"Format non supporté : {file_path}")

    # --- 2) Nettoyage des colonnes ---
    df.columns = df.columns.str.replace(" ", "")
    df.columns = df.columns.str.replace(".", "")
    df.columns = df.columns.str.replace("/", "")
    df.columns = normalize_and_dedup_columns(df.columns)

    print(df)
    return df


def normalize_and_dedup_columns(columns):
    seen = Counter()
    new_cols = []
    for col in columns:
        normed = normalize_column(col)  # ta fonction de normalisation
        seen[normed] += 1
        if seen[normed] == 1:
            new_cols.append(normed)
        else:
            new_cols.append(f"{normed}_{seen[normed]}")
    return new_cols


def normalize_column(name: str) -> str:
    reserved_word = Counter()
    name = name.strip().lower()  # lowercase + trim
    name = re.sub(r"[^0-9a-zA-Z_]+", "_", name)  # replace non-alphanum with "_"
    name = re.sub(r"_+", "_", name)  # collapse multiple "_"
    name = name.strip("_")  # remove leading/trailing "_"

    # si le nom est un mot réservé SQL → ajouter suffixe incrémental
    if name in PG_RESERVED:
        reserved_word[name] += 1
        name = f"{name}_{reserved_word[name]}"

    return name
