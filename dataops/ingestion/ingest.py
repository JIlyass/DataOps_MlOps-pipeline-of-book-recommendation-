"""
Script d'ingestion des données brutes (CSV) vers DuckDB en utilisant dlt.
Version compatible Windows (sans emojis).
Détecte automatiquement le séparateur CSV (',' ou ';').
"""
import csv
import dlt
from dlt.destinations import duckdb
import pandas as pd
from pathlib import Path

# --- Chemins ----------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw"
DUCKDB_PATH = PROJECT_ROOT / "data" / "book_recommender.duckdb"

print(f"[INFO] Donnees brutes : {RAW_DATA_PATH}")
print(f"[INFO] Base DuckDB    : {DUCKDB_PATH}")

# --- Pipeline dlt -----------------------------------------------------------
pipeline = dlt.pipeline(
    pipeline_name="book_recommender_pipeline",
    destination=duckdb(credentials=str(DUCKDB_PATH)),
    dataset_name="raw_data",
)


def detect_separator(file_path: Path) -> str:
    """Detecte le separateur CSV (',' ou ';') en lisant la premiere ligne."""
    with open(file_path, "r", encoding="latin-1", errors="replace") as f:
        first_line = f.readline()
    if first_line.count(";") > first_line.count(","):
        return ";"
    return ","


def read_csv_robust(file_path: Path) -> pd.DataFrame:
    """
    Lecture robuste d'un CSV Book-Crossing.
    - Detecte automatiquement le separateur
    - Essaie pandas engine='c' puis fallback csv.reader
    """
    sep = detect_separator(file_path)
    print(f"   Separateur detecte : '{sep}'")

    # --- Strategie 1 : pandas engine='c' ---
    try:
        print("   [TRY 1] pandas engine='c' ...")
        df = pd.read_csv(
            file_path,
            sep=sep,
            encoding="latin-1",
            engine="c",
            on_bad_lines="skip",
            low_memory=False,
        )
        if df.shape[1] > 1:
            print(f"   [OK] engine='c' -> shape {df.shape}")
            print(f"   Colonnes : {df.columns.tolist()}")
            return df
        print(f"   [WARN] engine='c' n'a lu que {df.shape[1]} colonne(s)")
    except Exception as e:
        print(f"   [WARN] engine='c' a echoue : {e}")

    # --- Strategie 2 : csv.reader (stdlib) ---
    print("   [TRY 2] csv.reader (stdlib) ...")
    rows = []
    with open(file_path, "r", encoding="latin-1", errors="replace", newline="") as f:
        reader = csv.reader(f, delimiter=sep, quotechar='"')
        header = next(reader)
        rows.append(header)
        for row in reader:
            if len(row) == len(header):
                rows.append(row)

    df = pd.DataFrame(rows[1:], columns=rows[0])
    print(f"   [OK] csv.reader -> shape {df.shape}")
    print(f"   Colonnes : {df.columns.tolist()}")
    return df


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace("-", "_", regex=False)
        .str.replace(" ", "_", regex=False)
        .str.replace(".", "_", regex=False)
    )
    return df


def load_csv_to_duckdb(file_path: Path, table_name: str):
    if not file_path.exists():
        raise FileNotFoundError(f"[ERROR] Fichier introuvable : {file_path}")

    print(f"\n[INFO] Chargement : {file_path.name} -> table '{table_name}'")
    df = read_csv_robust(file_path)
    df = normalize_columns(df)
    print(f"   Colonnes finales : {df.columns.tolist()}")

    load_info = pipeline.run(df, table_name=table_name, write_disposition="replace")
    print(f"   [OK] Charge dans raw_data.{table_name}")
    return load_info


if __name__ == "__main__":
    print("=" * 70)
    print("[START] Ingestion des donnees")
    print("=" * 70)

    load_csv_to_duckdb(RAW_DATA_PATH / "Books.csv", "books")
    load_csv_to_duckdb(RAW_DATA_PATH / "Users.csv", "users")
    load_csv_to_duckdb(RAW_DATA_PATH / "Ratings.csv", "ratings")

    print("\n" + "=" * 70)
    print("[DONE] Ingestion terminee avec succes !")
    print("=" * 70)