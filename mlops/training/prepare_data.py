import duckdb
import os
import pandas as pd
from sklearn.model_selection import train_test_split

def prepare_data():
    print("Démarrage de la préparation des données...")
    
    # Création du dossier cible pour les données séparées
    target_dir = os.path.join(os.path.dirname(__file__), "data")
    os.makedirs(target_dir, exist_ok=True)
    
    # Chemin vers la base de données DuckDB
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "book_recommender.duckdb"))
    
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"La base DuckDB est introuvable à {db_path}. Veuillez d'abord exécuter le pipeline DataOps.")
    
    print(f"Connexion à DuckDB ({db_path})...")
    # Connexion en lecture seule
    con = duckdb.connect(db_path, read_only=True)
    
    # Récupération des données nécessaires (user_id, isbn, book_rating)
    print("Extraction des données de la table main.books_enriched...")
    df = con.sql("SELECT user_id, isbn, book_rating FROM main.books_enriched").df()
    
    print(f"Données extraites : {len(df)} lignes.")
    
    # Séparation train/test (80/20)
    print("Séparation en ensembles d'entraînement (80%) et de test (20%)...")
    train, test = train_test_split(df, test_size=0.2, random_state=42)
    
    # Sauvegarde des fichiers
    train_path = os.path.join(target_dir, "train.csv")
    test_path = os.path.join(target_dir, "test.csv")
    
    train.to_csv(train_path, index=False)
    test.to_csv(test_path, index=False)
    
    print(f"Préparation terminée.")
    print(f"  - Train : {len(train)} lignes -> {train_path}")
    print(f"  - Test : {len(test)} lignes -> {test_path}")

if __name__ == "__main__":
    prepare_data()
