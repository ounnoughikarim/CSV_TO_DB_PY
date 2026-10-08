import polars as pl
from sqlalchemy import inspect, text
from csv_to_db_py.logger import logger
from csv_to_db_py.config import config
from csv_to_db_py.utils.cleaned_csv import quote_identifier


def _truncate_if_exists(engine, table_name, expected_columns):
    """TRUNCATE if table exists → preserve schema & dependent views. Returns True if truncated."""
    inspector = inspect(engine)
    if not inspector.has_table(table_name):
        return False
    db_columns = [column["name"] for column in inspector.get_columns(table_name)]
    if sorted(db_columns) != sorted(expected_columns):
        # ponytail: column-name drift is guarded; TYPE drift is not (still fails loudly after truncate)
        raise ValueError(
            f"Schema drift on table {table_name!r}: existing columns {sorted(db_columns)} "
            f"differ from CSV columns {sorted(expected_columns)}. "
            "DROP TABLE ... CASCADE and recreate dependent views, or align the CSV columns."
        )
    with engine.begin() as conn:
        conn.execute(text(f"TRUNCATE TABLE {quote_identifier(table_name)}"))
    return True


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
    - Parmi les valeurs "utiles" restantes, au moins `datetime_detection_threshold` doivent être des dates valides
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
        original_indices = (
            column.to_frame()
            .with_row_count("idx")
            .filter((column.is_not_null()) & (column.str.strip_chars() != ""))["idx"]
        )

        parsed_useful = parsed_col.gather(original_indices)
        parsed_useful = parsed_useful.filter(parsed_useful.is_not_null())
        num_parsed = len(parsed_useful)

        success_rate = num_parsed / num_useful

        # Si au moins la part configurée des valeurs utiles est parsée, on convertit
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
                pl.col(column_name).str.strptime(
                    pl.Datetime, format=date_format, strict=False
                )
            )

            # Same logic as above
            parsed_col = parsed[column_name]
            original_indices = (
                column.to_frame()
                .with_row_count("idx")
                .filter((column.is_not_null()) & (column.str.strip_chars() != ""))[
                    "idx"
                ]
            )

            parsed_useful = parsed_col.gather(original_indices)
            parsed_useful = parsed_useful.filter(parsed_useful.is_not_null())
            num_parsed = len(parsed_useful)
            success_rate = num_parsed / num_useful

            # Si au moins la part configurée des valeurs utiles est parsée, on accepte
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


def convert_datetime_columns(dataframe):
    """Convert every string column that looks like a date, using the configured detection threshold."""
    for column_name in dataframe.columns:
        dataframe = detect_and_parse_datetime_column(dataframe, column_name)
    return dataframe


def postgrestype_dict(dataframe, sample_size=10000):
    """
    Détermine les types PostgreSQL pour chaque colonne du DataFrame.

    Args:
        dataframe: DataFrame Polars
        sample_size: Taille maximale de l'échantillon pour l'analyse des types.
                     Si le DataFrame est plus grand, un échantillon aléatoire est utilisé.

    Returns:
        dict: Mapping {nom_colonne: type_postgresql}
    """
    column_types = {}

    # Use sample if dataframe is larger than sample_size
    num_rows = len(dataframe)
    if num_rows > sample_size:
        logger.info(
            f"DataFrame contient {num_rows} lignes. Utilisation d'un échantillon aléatoire "
            f"de {sample_size} lignes pour la détection des types."
        )
        df_sample = dataframe.sample(n=sample_size, seed=42)
    else:
        df_sample = dataframe

    for column_name in df_sample.columns:
        column_types[column_name] = map_polars_dtype_to_postgresql(
            df_sample[column_name]
        )

    return column_types


def overwrite_table_with_csv_data(engine, csv_data, table_name):
    # Convert polars DataFrame to pandas for SQLAlchemy compatibility
    pandas_data = csv_data.to_pandas()

    # Get batch size from config (default: 10000)
    batch_size = config.get("batch_size", 10000)
    total_rows = len(pandas_data)

    # Typed table always pre-created (create_table_from_csv raises on failure); to_sql only appends.
    truncated = _truncate_if_exists(engine, table_name, csv_data.columns)

    if total_rows <= batch_size:
        pandas_data.to_sql(name=table_name, con=engine, if_exists="append", index=False)
        logger.info(
            f"Table '{table_name}' {'vidée puis remplie' if truncated else 'créée'} "
            f"avec {total_rows} lignes (insertion unique)"
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

            batch_data.to_sql(
                name=table_name, con=engine, if_exists="append", index=False
            )

            logger.info(
                f"  Batch {batch_num}/{num_batches}: {len(batch_data)} lignes insérées "
                f"(lignes {i + 1} à {end_idx})"
            )

        logger.info(
            f"Insertion terminée: {total_rows} lignes insérées dans '{table_name}'"
        )
