
---

# 📘 HANDOVER — Passage DataOps → MLOps

**Projet :** Système de recommandation de livres (Book-Crossing)  
**Module :** MLOps & DataOps — Master 1ère année S2  
**Destinataire :** Camarade en charge de la partie MLOps  
**Émetteur :** Équipe DataOps

---

## 🎯 1. Contexte et objectif du projet

Le projet complet demande de construire un **système de recommandation de livres** industrialisé selon les principes **DataOps + MLOps + Agile**, comme décrit dans le PDF *Appel à Projets MLOps & DataOps*.

### Architecture cible (PDF, page 3)

```
Sources → dlt → DuckDB → dbt → Tests Qualité → Dagster → ML → MLflow → FastAPI → Docker → CI/CD → Monitoring
         [========== DATAOPS ==========]           [=========== MLOPS ===========]
```

- **DataOps** ✅ = fait (toi, aujourd'hui)
- **MLOps** 🎯 = à faire (ce camarade)

### Livrables obligatoires du PDF

| # | Livrable | Responsable |
|---|----------|-------------|
| 1 | Vision du projet | PO |
| 2 | Gestion Agile (3 sprints min) | Scrum Master |
| 3 | Dépôt GitHub | Tous |
| 4 | Pipeline DataOps (dlt + DuckDB + dbt + Dagster) | ✅ DataOps |
| 5 | Qualité des données (tests, contracts, lineage) | ✅ DataOps |
| 6 | Composant Machine Learning | ✅ MLOps |
| 7 | MLflow (tracking + registry) | ✅ MLOps |
| 8 | Déploiement (FastAPI + Docker) | ✅ MLOps |
| 9 | Déploiement Komodo | 🎯 MLOps |
| 10 | Monitoring (dispo, temps réponse, dérive) | ✅ MLOps |
| 11 | Documentation + Présentation | Tous |

---

## ✅ 2. Ce qui est déjà fait (DataOps)

### 2.1 Architecture DataOps en place

```
data/raw/*.csv  →  dlt  →  DuckDB  →  dbt  →  Tests  →  Dagster
```

Le pipeline complet est **100 % fonctionnel** et orchestration vérifiée via Dagster.

### 2.2 Structure du projet actuel

```
mlops_core_team_book_recommender/
├── data/
│   ├── raw/                              # Books.csv, Users.csv, Ratings.csv
│   └── book_recommender.duckdb           # Base DuckDB (généré)
│
├── dataops/
│   ├── ingestion/
│   │   └── ingest.py                     # Script dlt : CSV → DuckDB
│   │
│   ├── dbt_project/
│   │   └── book_transform/
│   │       ├── dbt_project.yml
│   │       ├── models/
│   │       │   ├── staging/
│   │       │   │   ├── stg_books.sql
│   │       │   │   ├── stg_users.sql
│   │       │   │   └── stg_ratings.sql
│   │       │   ├── marts/
│   │       │   │   ├── ratings_explicit.sql
│   │       │   │   ├── books_enriched.sql
│   │       │   │   └── top_books_by_ratings.sql
│   │       │   └── schema.yml            # Tests qualité dbt
│   │       └── target/                   # Généré par dbt
│   │
│   └── dagster_project/
│       └── book_pipeline/
│           └── book_pipeline/
│               ├── __init__.py
│               ├── assets.py             # 3 assets : raw_ingestion, dbt_run, dbt_test
│               └── definitions.py
│
├── mlops/                                # 🎯 À REMPLIR PAR LE CAMARADE
│   ├── training/
│   ├── api/
│   └── models/
│
├── docker/                               # 🎯 À REMPLIR
├── tests/                                # 🎯 À REMPLIR
├── notebooks/                            # Notebook original (référence)
├── .github/workflows/                    # 🎯 À REMPLIR
├── .gitignore
├── README.md
└── requirements.txt
```

### 2.3 Détail des composants DataOps

#### 🔹 Ingestion (`dataops/ingestion/ingest.py`)
- Lit les 3 CSV (`Books.csv`, `Users.csv`, `Ratings.csv`) depuis `data/raw/`
- **Détecte automatiquement le séparateur** (les CSV Book-Crossing utilisent `;` et non `,`)
- Charge dans DuckDB avec `write_disposition="replace"` dans le schéma `raw_data`
- Tables créées : `raw_data.books`, `raw_data.users`, `raw_data.ratings`

#### 🔹 dbt (`dataops/dbt_project/book_transform/`)
Profils configurés dans `C:\Users\<user>\.dbt\profiles.yml` :
```yaml
book_profile:
  target: dev
  outputs:
    dev:
      type: duckdb
      path: "D:/.../data/book_recommender.duckdb"
      threads: 1
```

Modèles dbt (ordre de dépendance) :
```
stg_books ────┐
stg_users ────┼──→ ratings_explicit ────→ books_enriched ────→ top_books_by_ratings
stg_ratings ──┘
```

**Tables finales disponibles pour le ML** (dans le schéma `main`) :
- `main.books_enriched` : **383 842 lignes** — user_id, isbn, book_rating (1-10), book_title, book_author, publisher, year_of_publication → **source principale pour l'entraînement**
- `main.ratings_explicit` : ratings explicites uniquement (1-10)
- `main.top_books_by_ratings` : baseline popularité (top livres par nb de ratings)

#### 🔹 Tests qualité (dbt)
```bash
cd dataops/dbt_project/book_transform
dbt test
```
Tests : `unique`, `not_null`, `accepted_values`, `relationships`.

#### 🔹 Data Lineage
```bash
dbt docs generate
dbt docs serve   # → http://localhost:8080
```

#### 🔹 Dagster (orchestration)
3 assets en série :
```
raw_ingestion (dlt) → dbt_run → dbt_test
```
Lancement :
```bash
cd dataops/dagster_project/book_pipeline
dagster dev -m book_pipeline.definitions
# → http://localhost:3000
# Cliquer sur "Materialize all"
```

### 2.4 Environnement technique

- **OS** : Windows 11
- **IDE** : VS Code
- **Python** : Anaconda (`C:\Users\lenovo\anaconda3\python.exe`)
- **Environnement virtuel** : `.venv` à la racine (mais les commandes `dbt` et `dagster` tournent avec Anaconda)
- **Base** : DuckDB (fichier local `data/book_recommender.duckdb`)

### 2.5 ⚠️ Pièges rencontrés (à connaître absolument !)

Ces problèmes ont déjà été résolus — le camarade MLOps doit les connaître pour ne pas retomber dedans.

| # | Symptôme | Cause | Solution appliquée |
|---|----------|-------|-------------------|
| 1 | Colonne concaténée `isbn_book_title_..._x` | pandas ne détectait pas le séparateur | Détection auto du séparateur (`;` vs `,`) |
| 2 | `UnicodeEncodeError: 'charmap'` | Emojis dans `print()` + cp1252 Windows | Retrait emojis + `PYTHONUTF8=1` dans subprocess |
| 3 | `TypeError: pipeline got unexpected keyword 'credentials'` | Mauvaise API dlt | `destination=duckdb(credentials=...)` |
| 4 | `EmptyDataError: No columns to parse` | Mauvais séparateur | Détection auto `;` |
| 5 | Dagster ne trouve pas d'assets | `assets.py` incomplet | Fichier complet avec les 3 `@asset` |
| 6 | `dbt debug` : profil introuvable | `profiles.yml` absent dans `~/.dbt/` | Créé manuellement dans `C:\Users\<user>\.dbt\profiles.yml` |

### 2.6 Ce que tu peux réutiliser immédiatement

- ✅ **`main.books_enriched`** : c'est LA table à utiliser pour l'entraînement ML
- ✅ **Structure dbt** : déjà en place, tu peux ajouter des modèles pour préparer le train/test split si tu veux
- ✅ **Dagster** : tu peux ajouter de nouveaux assets pour le ML (ex: `train_svd_model`, `evaluate_model`) qui dépendront de `dbt_test`
- ✅ **Structure de dossiers** : `mlops/training/`, `mlops/api/`, `mlops/models/`, `docker/`, `.github/workflows/` sont déjà créés (vides)

---

## 🎯 3. Ce que tu (camarade MLOps) dois faire

### 3.1 Roadmap MLOps (alignée sur le PDF)

| Étape | Livrable PDF | Description |
|-------|-------------|-------------|
| **M1** | ✅ Composant ML | Préparation données + entraînement + évaluation |
| **M2** | ✅ MLflow | Tracking + Registry |
| **M3** | ✅ FastAPI | `/predict` + `/health` |
| **M4** | ✅ Docker | Conteneurisation |
| **M7** | ✅ Monitoring | Disponibilité + latence + dérive |
| **M5** | 🎯 Komodo | Déploiement |

---

### 3.2 Étape M1 — Préparation des données

**Source** : table `main.books_enriched` dans DuckDB.

```python
import duckdb
con = duckdb.connect("data/book_recommender.duckdb", read_only=True)
df = con.sql("SELECT user_id, isbn, book_rating FROM main.books_enriched").df()
```

**Split train/test** : 80/20, comme dans le notebook original.

```python
from sklearn.model_selection import train_test_split
train, test = train_test_split(df, test_size=0.2, random_state=42)
```

Créer `mlops/training/prepare_data.py` qui :
1. Se connecte à DuckDB
2. Charge `books_enriched`
3. Split 80/20
4. Sauvegarde `train.csv` et `test.csv` dans `mlops/training/data/`

---

### 3.3 Étape M2 — Entraînement + MLflow

**Modèle recommandé** : SVD (`scikit-surprise`) — c'est celui du notebook et il obtient le meilleur RMSE (1.64).

⚠️ Si `scikit-surprise` pose problème sur Windows, alternatives :
- `surprise` via `pip install scikit-surprise`
- Sinon utiliser `SVD` de `scikit-learn` (moins performant mais fonctionne)

**Structure du script** `mlops/training/train.py` :

```python
import mlflow
import mlflow.sklearn
from surprise import SVD, Dataset, Reader, accuracy
from surprise.model_selection import train_test_split
import pandas as pd
import duckdb

# 1. Connexion à MLflow
mlflow.set_tracking_uri("http://localhost:5000")  # serveur MLflow (docker/Komodo)
mlflow.set_experiment("book-recommender-svd")

# 2. Charger les données
con = duckdb.connect("data/book_recommender.duckdb", read_only=True)
df = con.sql("SELECT user_id, isbn, book_rating FROM main.books_enriched").df()

# 3. Split
reader = Reader(rating_scale=(1, 10))
data = Dataset.load_from_df(df[["user_id", "isbn", "book_rating"]], reader)
trainset, testset = train_test_split(data, test_size=0.2, random_state=42)

# 4. Entraînement avec MLflow tracking
with mlflow.start_run(run_name="svd_baseline"):
    # Hyperparamètres
    params = {"n_factors": 100, "n_epochs": 20, "lr_all": 0.005, "reg_all": 0.02}
    mlflow.log_params(params)

    model = SVD(**params, random_state=42)
    model.fit(trainset)

    # Évaluation
    predictions = model.test(testset)
    rmse = accuracy.rmse(predictions)
    mlflow.log_metric("rmse", rmse)

    # Sauvegarde du modèle
    mlflow.sklearn.log_model(model, "model", registered_model_name="book-recommender-svd")

print(f"✅ RMSE = {rmse:.4f}")
```

**Livrables M2** :
- Serveur MLflow en marche (voir M5 pour Docker/Komodo)
- Experiment `book-recommender-svd` visible dans l'UI MLflow
- Modèle enregistré dans le Registry
- RMSE loggé (~1.64 attendu)

---

### 3.4 Étape M3 — API FastAPI

**Fichier** `mlops/api/main.py` :

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mlflow
import duckdb
from surprise import SVD

app = FastAPI(title="Book Recommender API")

# Charger le modèle depuis MLflow au démarrage
mlflow.set_tracking_uri("http://mlflow:5000")
MODEL_URI = "models:/book-recommender-svd/Production"
model = mlflow.sklearn.load_model(MODEL_URI)

class PredictionRequest(BaseModel):
    user_id: int
    isbn: str

class PredictionResponse(BaseModel):
    user_id: int
    isbn: str
    predicted_rating: float

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/predict", response_model=PredictionResponse)
def predict(req: PredictionRequest):
    try:
        pred = model.predict(req.user_id, req.isbn)
        return PredictionResponse(
            user_id=req.user_id,
            isbn=req.isbn,
            predicted_rating=float(pred.est)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

**Tests locaux** :
```bash
uvicorn mlops.api.main:app --reload --port 8000
# http://localhost:8000/health
# http://localhost:8000/docs (Swagger)
curl -X POST http://localhost:8000/predict -H "Content-Type: application/json" -d '{"user_id": 276744, "isbn": "038550120X"}'
```

---

### 3.5 Étape M4 — Dockerisation

**Fichier** `docker/Dockerfile.api` :

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY mlops/ ./mlops/
COPY data/book_recommender.duckdb ./data/

EXPOSE 8000

CMD ["uvicorn", "mlops.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Fichier** `docker-compose.yml` (à la racine) :

```yaml
version: "3.9"
services:
  mlflow:
    image: ghcr.io/mlflow/mlflow:latest
    ports:
      - "5000:5000"
    command: mlflow server --host 0.0.0.0 --port 5000 --backend-store-uri sqlite:///mlflow.db --default-artifact-root /mlartifacts
    volumes:
      - ./mlflow_data:/mlartifacts

  api:
    build:
      context: .
      dockerfile: docker/Dockerfile.api
    ports:
      - "8000:8000"
    depends_on:
      - mlflow
    environment:
      - MLFLOW_TRACKING_URI=http://mlflow:5000
```

**Build et test local** :
```bash
docker-compose up --build
```

---

### 3.6 Étape M5 — Déploiement sur Komodo

Ton dashboard **Komodo** (déjà fourni par le prof) permet de gérer des conteneurs Docker. Voici comment déployer :

1. Se connecter à Komodo : `http://<ton-serveur-komodo>:9120`
2. Aller dans **Stacks** → cliquer sur **Create Stack**
3. Nom : `book-recommender`
4. Ajouter les services :
   - `mlflow` (port 5000)
   - `api` (port 8000)
5. Configurer les variables d'environnement et les volumes
6. **Démarrer la Stack** → vérifier que les conteneurs passent à `Healthy`

**Livrables M5** :
- Capture d'écran Komodo avec les 2 conteneurs verts
- URL publique de l'API

---

### 3.7 Étape M6 — CI/CD GitHub Actions

**Fichier** `.github/workflows/ci.yml` :

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest
      - name: Run tests
        run: pytest tests/ -v
      - name: Lint
        run: |
          pip install ruff
          ruff check .

  build-docker:
    runs-on: ubuntu-latest
    needs: test
    steps:
      - uses: actions/checkout@v4
      - name: Build API image
        run: docker build -f docker/Dockerfile.api -t book-api:${{ github.sha }} .
```

**Tests à ajouter dans `tests/`** :
- `test_ingestion.py` : vérifie que les CSV sont bien chargés
- `test_dbt_models.py` : vérifie que les modèles dbt compilent
- `test_api.py` : teste `/health` et `/predict` (avec TestClient)

---

### 3.8 Étape M7 — Monitoring

À mettre en place :

1. **Disponibilité service** : endpoint `/health` + Healthcheck Docker
2. **Temps de réponse** : middleware FastAPI qui log la latence
3. **Métriques ML** : RMSE tracé dans MLflow à chaque run
4. **Dérive simple** : comparer la distribution des prédictions vs réelle (script périodique)

Ajouter un middleware :

```python
import time
from fastapi import Request

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    response.headers["X-Process-Time"] = str(duration)
    # logger duration dans un fichier / Prometheus
    return response
```

---

## 📦 4. Dépendances à ajouter au projet

Compléter `requirements.txt` avec :

```txt
# MLOps
mlflow==2.18.0
scikit-surprise==1.1.4
fastapi==0.115.0
uvicorn[standard]==0.32.0
pydantic==2.9.2

# Tests
pytest==8.3.3
httpx==0.27.2
ruff==0.7.0
```

---

## 🔧 5. Commandes utiles (à connaître par cœur)

```bash
# Activer l'environnement
.venv\Scripts\activate

# Ingestion (si besoin de refaire)
python dataops/ingestion/ingest.py

# dbt
cd dataops/dbt_project/book_transform
dbt run
dbt test
dbt docs serve

# Dagster
cd dataops/dagster_project/book_pipeline
dagster dev -m book_pipeline.definitions

# MLflow (local)
mlflow ui --port 5000

# API (local)
uvicorn mlops.api.main:app --reload --port 8000

# Docker
docker-compose up --build
docker-compose logs -f api
```

---

## 🎓 6. Bonnes pratiques à respecter (PDF)

- ✅ **Git** : commits fréquents, branches par feature, Pull Requests
- ✅ **Agile** : 3 sprints minimum, Product Backlog, User Stories, Sprint Review + Retro
- ✅ **Data Contracts** : schémas YAML des tables (à étendre pour les tables ML)
- ✅ **Data Lineage** : `dbt docs` + graphe Dagster
- ✅ **Versionnement** : tag Git pour chaque version du modèle (ex: `v1.0.0-model-svd`)
- ✅ **Reproductibilité** : `requirements.txt` + Docker + seeds fixés

---

## 📅 7. Planning suggéré (Agile)

| Sprint | Durée | Contenu |
|--------|-------|---------|
| **Sprint 1** | 1 semaine | Préparation données + entraînement SVD + MLflow tracking |
| **Sprint 2** | 1 semaine | FastAPI + Docker + tests |
| **Sprint 3** | 1 semaine | Komodo + CI/CD + Monitoring + Documentation |
| **Final** | — | Rapport + Présentation (15 min) + Démo (10 min) |

---

## 🚨 8. Points d'attention

1. **Ne pas modifier** les fichiers DataOps sans prévenir — le pipeline doit rester stable.
2. **Toujours tester en local** avant de pousser sur GitHub.
3. **Utiliser des variables d'environnement** pour les URLs (MLflow, DuckDB) — jamais de valeurs en dur.
4. **Ne pas commiter** les fichiers `.duckdb`, `mlruns/`, `models/*.pkl` (voir `.gitignore`).
5. **Communiquer avec l'équipe DataOps** avant de modifier les schémas dbt ou les assets Dagster.

---

## 📞 9. Contact / Questions

- **DataOps** : [ton nom + contact]
- **Repo GitHub** : [URL]
- **Dashboard Komodo** : [URL]
- **Documentation dbt** : `dbt docs serve` en local

---

## ✅ 10. Checklist finale avant livraison

- [x] Modèle Scikit-Learn entraîné et loggé dans MLflow
- [x] MLflow Registry : modèle enregistré
- [x] API FastAPI : `/health` et `/predict` fonctionnels
- [x] Dockerfile API + docker-compose (MLflow + API)
- [x] Monitoring : `/health` + latence + RMSE dans MLflow
- [ ] Stack Komodo déployée avec conteneurs Healthy
- [x] README à jour avec architecture complète
- [ ] 3 Sprints documentés (Backlog, Reviews, Retros)
- [ ] Présentation finale (15 min) + Démo (10 min) préparées

---

**Bon courage ! La partie DataOps est solide, la partie MLOps est maintenant balisée étape par étape.** 🚀
