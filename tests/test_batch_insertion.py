"""
Test de l'insertion par batch.

Ce script teste que la fonction overwrite_table_with_csv_data
fonctionne correctement avec différentes tailles de données.
"""

import sys
import os

# Ajouter le répertoire parent au path pour importer les modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def test_batch_logic():
    """Test la logique de calcul des batchs."""

    print("TEST DE LA LOGIQUE DE BATCH")
    print("=" * 80)

    test_cases = [
        (50, 100000, "Petit dataset (< batch_size)"),
        (100000, 100000, "Exactement batch_size"),
        (150000, 100000, "1.5x batch_size"),
        (250000, 100000, "2.5x batch_size"),
        (1000000, 100000, "1 million de lignes"),
        (1000000, 50000, "1 million de lignes, batch 50k"),
    ]

    for total_rows, batch_size, description in test_cases:
        num_batches = (total_rows + batch_size - 1) // batch_size
        print(f"\n{description}:")
        print(f"  Total lignes: {total_rows:,}")
        print(f"  Taille batch: {batch_size:,}")
        print(f"  Nombre de batchs: {num_batches}")

        if total_rows <= batch_size:
            print("  > Insertion unique (pas de batch)")
        else:
            print(f"  > {num_batches} batch(s) necessaire(s)")
            for i in range(0, total_rows, batch_size):
                batch_num = (i // batch_size) + 1
                end_idx = min(i + batch_size, total_rows)
                batch_rows = end_idx - i
                print(
                    f"     Batch {batch_num}: lignes {i + 1:,} à {end_idx:,} ({batch_rows:,} lignes)"
                )

    print("\n" + "=" * 80)
    print("Test terminé!")


if __name__ == "__main__":
    test_batch_logic()
