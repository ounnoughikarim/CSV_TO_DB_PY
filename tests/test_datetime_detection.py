"""
Test de détection automatique des formats de dates.

Ce script teste la fonction detect_and_parse_datetime_column sur un fichier CSV
contenant différents formats de dates internationaux.
"""

import sys
import os
import logging
import polars as pl

# Ajouter le répertoire parent au path pour importer les modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Configure logging avant d'importer les modules
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def detect_and_parse_datetime_column(dataframe, column_name):
    """
    Détecte automatiquement si une colonne string contient des dates et trouve le format approprié.
    Version standalone pour les tests.
    """
    column = dataframe[column_name]
    dtype_str = str(column.dtype)

    # Only process string columns
    if "Utf8" not in dtype_str and "String" not in dtype_str:
        return dataframe

    # Filter out nulls AND empty strings
    useful_values = column.filter(
        (column.is_not_null()) & (column.str.strip_chars() != "")
    )

    num_useful = len(useful_values)
    if num_useful == 0:
        return dataframe

    # Seuil : au moins 70% des valeurs utiles doivent être parsées comme dates
    MIN_SUCCESS_RATE = 0.7

    # Try automatic datetime parsing with Polars
    try:
        parsed = dataframe.with_columns(
            pl.col(column_name).str.to_datetime(strict=False)
        )

        parsed_col = parsed[column_name]
        original_indices = (
            column.to_frame()
            .with_row_count("idx")
            .filter((column.is_not_null()) & (column.str.strip_chars() != ""))["idx"]
        )

        parsed_useful = parsed_col.gather(original_indices)
        parsed_useful = parsed_useful.filter(parsed_useful.is_not_null())
        num_parsed = len(parsed_useful)
        success_rate = num_parsed / num_useful

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

    # Try common date formats manually
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
        "%Y%m%d",
        "%Y%m%d%H%M%S",
    ]

    for date_format in common_formats:
        try:
            parsed = dataframe.with_columns(
                pl.col(column_name).str.strptime(
                    pl.Datetime, format=date_format, strict=False
                )
            )

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

    return dataframe


def print_separator():
    print("\n" + "=" * 80 + "\n")


def test_datetime_detection():
    """Test la détection automatique des formats de dates."""

    # Charger le fichier CSV de test
    test_file = os.path.join(os.path.dirname(__file__), "date_formats_test.csv")

    print("TEST DE DETECTION AUTOMATIQUE DES FORMATS DE DATES")
    print_separator()

    # Afficher le seuil de détection utilisé
    print("Configuration du test : seuil de detection = 70% (0.7)")
    print(
        "Note: Par defaut dans mainConfig.json, le seuil est 100% (1.0) pour desactiver la detection automatique"
    )
    print_separator()

    print(f"Lecture du fichier de test : {test_file}")
    df = pl.read_csv(test_file)

    print(f"\nDataframe original ({len(df)} lignes, {len(df.columns)} colonnes)")
    print(f"Colonnes : {', '.join(df.columns)}")
    print_separator()

    # Afficher un aperçu des données originales
    print("Apercu des donnees originales (3 premieres lignes) :")
    print(f"  Shape: {df.shape}")
    print_separator()

    # Tester la détection pour chaque colonne
    print("TEST DE DETECTION PAR COLONNE")
    print_separator()

    results = []

    for column_name in df.columns:
        print(f"\nColonne : {column_name}")
        col_dtype = str(df[column_name].dtype)
        print(f"   Type original : {col_dtype}")

        # Compter les valeurs utiles (non-nulles et non-vides)
        # Pour les colonnes string seulement
        if "Utf8" in col_dtype or "String" in col_dtype:
            useful_values = df[column_name].filter(
                (df[column_name].is_not_null())
                & (df[column_name].str.strip_chars() != "")
            )
        else:
            useful_values = df[column_name].filter(df[column_name].is_not_null())

        num_useful = len(useful_values)
        num_null = len(df) - len(df[column_name].drop_nulls())

        print(f"   Valeurs utiles : {num_useful}/{len(df)} ({num_null} nulls)")

        # Tester la détection
        df_parsed = detect_and_parse_datetime_column(df.clone(), column_name)
        new_type = df_parsed[column_name].dtype

        detected = "Datetime" in str(new_type) or "Date" in str(new_type)

        if detected:
            print(f"   [OK] DETECTE comme datetime : {new_type}")
            # Compter combien ont été parsées
            parsed_values = df_parsed[column_name].filter(
                df_parsed[column_name].is_not_null()
            )
            print(f"   {len(parsed_values)} valeurs parsees avec succes")
        else:
            print(f"   [X] NON DETECTE (reste {new_type})")

        results.append(
            {
                "colonne": column_name,
                "détecté": detected,
                "type_original": str(df[column_name].dtype),
                "type_final": str(new_type),
                "valeurs_utiles": num_useful,
                "nulls": num_null,
            }
        )

        print("-" * 80)

    # Résumé final
    print_separator()
    print("RESUME DES RESULTATS")
    print_separator()

    detected_count = sum(1 for r in results if r["détecté"])
    total_count = len(results)

    print(f"Colonnes detectees comme datetime : {detected_count}/{total_count}")
    print()

    for result in results:
        status = "[OK]" if result["détecté"] else "[X]"
        print(
            f"{status} {result['colonne']:20s} | {result['type_original']:10s} -> {result['type_final']:20s} | "
            f"{result['valeurs_utiles']} valeurs utiles, {result['nulls']} nulls"
        )

    print_separator()

    # Afficher le dataframe final avec toutes les colonnes converties
    print("DATAFRAME FINAL (avec detection appliquee sur toutes les colonnes)")
    print_separator()

    df_final = df.clone()
    for column_name in df_final.columns:
        df_final = detect_and_parse_datetime_column(df_final, column_name)

    print(f"  Shape final: {df_final.shape}")
    print(f"  Types: {dict(zip(df_final.columns, [str(t) for t in df_final.dtypes]))}")
    print_separator()

    print("Test termine !")
    print()

    return results


if __name__ == "__main__":
    results = test_datetime_detection()
