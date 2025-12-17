import polars as pl
import psycopg2
from logger import logger
from csv_to_db_py.config import config


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


def detect_and_parse_datetime_column(dataframe, column_name):
    """
    Détecte automatiquement si une colonne string contient des dates et trouve le format approprié.
    Utilise l'inférence automatique de Polars qui supporte de nombreux formats.

    Logique de validation:
    - Filtre les nulls et chaînes vides (valeurs non significatives pour l'analyse)
    - Parmi les valeurs "utiles" restantes, au moins 90% doivent être des dates valides
    - Les valeurs invalides sont converties en null automatiquement (strict=False)
    - Préserve tous les nulls et chaînes vides originaux
    """
    column = dataframe[column_name]
    dtype_str = str(column.dtype)

    # Only process string columns
    if "Utf8" not in dtype_str and "String" not in dtype_str:
        return dataframe

    # Filter out nulls AND empty strings from original data
    # Ces valeurs ne sont pas significatives pour déterminer si c'est une colonne de dates
    useful_values = column.filter(
        (column.is_not_null()) & (column.str.strip_chars() != "")
    )

    num_useful = len(useful_values)
    if num_useful == 0:
        return dataframe

    # Seuil configurable pour la détection de dates (défaut: 1.0 = 100%, désactivé)
    MIN_SUCCESS_RATE = config.get("datetime_detection_threshold", 1.0)

    # Try automatic datetime parsing with Polars (supports many formats automatically)
    try:
        # Polars can auto-detect many datetime formats
        # strict=False means invalid values become null instead of raising errors
        parsed = dataframe.with_columns(
            pl.col(column_name).str.to_datetime(strict=False)
        )

        # Count how many useful values were successfully parsed as dates
        # On compte les dates parsées DANS LE DATAFRAME ORIGINAL (pour exclure les nulls initiaux)
        parsed_col = parsed[column_name]

        # On doit compter combien de valeurs utiles ont été converties en dates
        # Pour cela, on regarde la colonne parsée aux mêmes positions que les valeurs utiles
        original_indices = column.to_frame().with_row_count("idx").filter(
            (column.is_not_null()) & (column.str.strip_chars() != "")
        )["idx"]

        parsed_useful = parsed_col.gather(original_indices)
        parsed_useful = parsed_useful.filter(parsed_useful.is_not_null())
        num_parsed = len(parsed_useful)

        success_rate = num_parsed / num_useful

        # Si au moins 90% des valeurs utiles sont parsées comme dates, on convertit
        if success_rate >= MIN_SUCCESS_RATE:
            num_invalid = num_useful - num_parsed
            logger.info(
                f"Colonne '{column_name}' détectée comme datetime (format auto-détecté) - "
                f"{num_parsed}/{num_useful} valeurs utiles parsées ({success_rate:.1%}), "
                f"{num_invalid} valeur(s) invalide(s) convertie(s) en null"
            )
            return parsed
    except Exception as e:
        logger.debug(f"Auto-détection datetime échouée pour '{column_name}': {e}")

    # Try common date formats manually if auto-detection fails
    common_formats = [
        # ISO formats (YYYY-MM-DD)
        "%Y-%m-%d",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",

        # French/European formats (DD/MM/YYYY)
        "%d/%m/%Y",
        "%d/%m/%Y %H:%M:%S",
        "%d/%m/%y",

        # American formats (MM/DD/YYYY) - with AM/PM support
        "%m/%d/%Y",
        "%m/%d/%Y %H:%M:%S",
        "%m/%d/%Y %I:%M:%S %p",  # 12-hour format with AM/PM

        # European dot format (DD.MM.YYYY)
        "%d.%m.%Y",
        "%d.%m.%Y %H:%M:%S",

        # Other formats
        "%d-%m-%Y",
        "%d-%m-%Y %H:%M:%S",
        "%d-%m-%y",
        "%Y/%m/%d",
        "%Y/%m/%d %H:%M:%S",
    ]

    for date_format in common_formats:
        try:
            # strict=False: invalid values become null
            parsed = dataframe.with_columns(
                pl.col(column_name).str.strptime(pl.Datetime, format=date_format, strict=False)
            )

            # Same logic as above
            parsed_col = parsed[column_name]
            original_indices = column.to_frame().with_row_count("idx").filter(
                (column.is_not_null()) & (column.str.strip_chars() != "")
            )["idx"]

            parsed_useful = parsed_col.gather(original_indices)
            parsed_useful = parsed_useful.filter(parsed_useful.is_not_null())
            num_parsed = len(parsed_useful)
            success_rate = num_parsed / num_useful

            # Si au moins 90% des valeurs utiles sont parsées, on accepte
            if success_rate >= MIN_SUCCESS_RATE:
                num_invalid = num_useful - num_parsed
                logger.info(
                    f"Colonne '{column_name}' détectée comme datetime (format: {date_format}) - "
                    f"{num_parsed}/{num_useful} valeurs utiles parsées ({success_rate:.1%}), "
                    f"{num_invalid} valeur(s) invalide(s) convertie(s) en null"
                )
                return parsed
        except Exception:
            continue

    # If no format worked, return original dataframe
    # Les nulls et valeurs vides sont préservés dans tous les cas
    return dataframe


def postgrestype_dict(dataframe):
    # Lecture des noms de colonnes à partir du fichier
    column_types = {}

    # First pass: detect and convert datetime columns
    for column_name in dataframe.columns:
        dataframe = detect_and_parse_datetime_column(dataframe, column_name)

    # Second pass: map types to PostgreSQL
    for column_name in dataframe.columns:
        column_types[column_name] = map_polars_dtype_to_postgresql(
            dataframe[column_name]
        )

    return column_types


def overwrite_table_with_csv_data(engine, csv_data, table_name):
    try:
        # Convert polars DataFrame to pandas for SQLAlchemy compatibility
        pandas_data = csv_data.to_pandas()

        # Get batch size from config (default: 100000)
        batch_size = config.get("batch_size", 100000)
        total_rows = len(pandas_data)

        if total_rows <= batch_size:
            # Single batch insertion
            pandas_data.to_sql(name=table_name, con=engine, if_exists="replace", index=False)
            logger.info(
                f"Table '{table_name}' écrasée avec {total_rows} lignes (insertion unique)"
            )
        else:
            # Multi-batch insertion
            num_batches = (total_rows + batch_size - 1) // batch_size  # Ceiling division
            logger.info(
                f"Insertion de {total_rows} lignes dans '{table_name}' par batch de {batch_size} "
                f"({num_batches} batch(s))"
            )

            for i in range(0, total_rows, batch_size):
                batch_num = (i // batch_size) + 1
                end_idx = min(i + batch_size, total_rows)
                batch_data = pandas_data.iloc[i:end_idx]

                # First batch: replace table, subsequent batches: append
                if_exists = "replace" if i == 0 else "append"
                batch_data.to_sql(name=table_name, con=engine, if_exists=if_exists, index=False)

                logger.info(
                    f"  Batch {batch_num}/{num_batches}: {len(batch_data)} lignes insérées "
                    f"(lignes {i+1} à {end_idx})"
                )

            logger.info(f"Insertion terminée: {total_rows} lignes insérées dans '{table_name}'")

    except psycopg2.Error as e:
        logger.error(
            f"Erreur lors de l'écriture des données dans la table '{table_name}': {e}"
        )
    except Exception as e:
        logger.error(
            f"Erreur inattendue lors de l'écriture dans '{table_name}': {e}"
        )
