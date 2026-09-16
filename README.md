# MLOps Core Team — Book Recommender

Système de recommandation de livres basé sur le dataset **Book-Crossing**, construit dans le cadre du module **MLOps & DataOps**.

## 🏗️ Architecture DataOps
CSV (data/raw) → dlt → DuckDB → dbt → Tests qualité → Dagster

text

## 📂 Structure du projet
mlops_core_team_book_recommender/
├── data/
│ ├── raw/ # CSV bruts (Books, Users, Ratings)
│ └── book_recommender.duckdb # Base DuckDB
├── dataops/
│ ├── ingestion/ # Script dlt
│ ├── dbt_project/book_transform # Projet dbt (staging + marts)
│ └── dagster_project/book_pipeline # Orchestration Dagster
├── mlops/ # MLflow, FastAPI, modèles (à venir)
├── docker/ # Dockerfiles (à venir)
├── tests/ # Tests unitaires
└── .github/workflows/ # CI/CD (à venir)

text

## 🚀 Installation

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
▶️ Lancer le pipeline DataOps
1. Ingestion (dlt → DuckDB)
bash
python dataops/ingestion/ingest.py
2. Transformations dbt
bash
cd dataops/dbt_project/book_transform
dbt run
dbt test
dbt docs generate
dbt docs serve   # → http://localhost:8080
3. Orchestration Dagster
bash
cd dataops/dagster_project/book_pipeline
dagster dev -m book_pipeline.definitions
Puis ouvrir http://localhost:3000 et cliquer sur Materialize all.

🧱 Modèles dbt
Modèle	Type	Description
stg_books	view	Livres nettoyés (staging)
stg_users	view	Utilisateurs nettoyés
stg_ratings	view	Ratings nettoyés
ratings_explicit	table	Ratings explicites (1–10)
books_enriched	table	Fusion ratings + livres
top_books_by_ratings	table	Top livres par nombre de ratings
📊 Tests qualité
bash
cd dataops/dbt_project/book_transform
dbt test
Tests : unique, not_null, accepted_values, relationships.

🎯 État MLOps
✅ Entraînement Modèle (scikit-learn)
✅ MLflow : tracking + registry
✅ FastAPI (/predict, /health)
✅ Dockerisation locale
✅ Monitoring (temps de réponse et disponibilité)
□ Déploiement sur Komodo
👥 Équipe
MLOps Core Team — Projet Master 1ère année S2.

text

---

## 🎯 Résumé visuel : où tu en es
DATAOPS ✅✅✅✅✅✅✅✅ 100%
├── dlt ✅
├── DuckDB ✅
├── dbt ✅
├── Tests qualité ✅
├── Data Lineage ✅
├── Dagster ✅
└── README+gitignore ← 2 min, il te reste ça

MLOPS ✅✅✅✅✅✅⬜⬜ 80%
├── Entraînement Scikit-Learn ✅
├── MLflow (Tracking & Registry) ✅
├── FastAPI (API Rest) ✅
├── Docker (Compose) ✅
├── Monitoring ✅
└── Komodo ⬜

text

---