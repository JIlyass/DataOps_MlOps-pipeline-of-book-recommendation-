"""
Script utilitaire : téléchargement des données brutes Book-Crossing.
Source : http://www2.informatik.uni-freiburg.de/~cziegler/BX/
À utiliser si le dossier data/raw/ est vide.
"""
from pathlib import Path
from urllib.request import urlretrieve
import zipfile

DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"
DATA_DIR.mkdir(parents=True, exist_ok=True)

URL = "http://www2.informatik.uni-freiburg.de/~cziegler/BX/BX-CSV-Dump.zip"
ZIP_PATH = DATA_DIR / "BX-CSV-Dump.zip"

print(f"[INFO] Téléchargement : {URL}")
urlretrieve(URL, ZIP_PATH)

print(f"[INFO] Extraction dans : {DATA_DIR}")
with zipfile.ZipFile(ZIP_PATH, "r") as z:
    z.extractall(DATA_DIR)

# Renommage
renames = {
    "BX-Books.csv": "Books.csv",
    "BX-Users.csv": "Users.csv",
    "BX-Book-Ratings.csv": "Ratings.csv",
}
for old, new in renames.items():
    old_path = DATA_DIR / old
    new_path = DATA_DIR / new
    if old_path.exists() and not new_path.exists():
        old_path.rename(new_path)
        print(f"   {old} -> {new}")

ZIP_PATH.unlink()
print("[OK] Données prêtes dans data/raw/")