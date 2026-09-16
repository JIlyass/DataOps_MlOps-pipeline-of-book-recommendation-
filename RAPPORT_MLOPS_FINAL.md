# 🚀 Rapport de Fin de Projet MLOps - Système de Recommandation de Livres

Ce document sert de README détaillé et de document de passation (handover) pour la partie **MLOps** du projet de système de recommandation de livres (Book-Crossing). Il résume l'ensemble des tâches accomplies pour prendre le relais de la partie DataOps et industrialiser le modèle de Machine Learning.

---

## 🎯 Objectif du Module MLOps
Prendre la suite du pipeline DataOps (dlt + DuckDB + dbt) pour :
1. Préparer les données pour l'apprentissage.
2. Entraîner un modèle de recommandation.
3. Tracker les expérimentations et versionner le modèle.
4. Exposer le modèle via une API REST.
5. Conteneuriser l'application.
6. Mettre en place un monitoring (disponibilité, latence, dérive).

---

## ✅ Ce qui a été réalisé en détails

### 1. Préparation des Données (`mlops/training/prepare_data.py`)
- **Connexion à DuckDB :** Le script se connecte à la base de données DuckDB (`book_recommender.duckdb`) générée par l'équipe DataOps.
- **Extraction :** Il extrait la table `main.books_enriched` qui contient les données nettoyées et enrichies.
- **Split Train/Test :** Les données sont divisées aléatoirement en un ensemble d'entraînement (80%) et un ensemble de test (20%).
- **Sauvegarde :** Les ensembles sont sauvegardés sous forme de fichiers CSV (`train.csv` et `test.csv`) dans `mlops/training/data/` pour garantir la reproductibilité de l'entraînement.

### 2. Entraînement du Modèle & Tracking MLflow (`mlops/training/train.py`)
- **Pipeline Scikit-Learn :** Création d'un pipeline d'apprentissage machine utilisant un `OrdinalEncoder` (pour gérer les IDs utilisateurs et livres) et un modèle de régression `Ridge`.
- **Intégration MLflow :**
  - Connexion à un serveur de tracking local (`http://localhost:5000`).
  - Enregistrement des hyperparamètres (ex: `alpha`).
  - Calcul et enregistrement des métriques d'évaluation (RMSE sur le jeu de test).
- **Model Registry :** Le modèle entraîné est sauvegardé et enregistré automatiquement dans le MLflow Model Registry sous le nom `book-recommender-model`.

### 3. API de Prédiction FastAPI (`mlops/api/main.py`)
- **Framework :** Utilisation de FastAPI pour créer une API REST performante.
- **Endpoints :**
  - `/health` : Vérifie que l'API est en ligne (Healthcheck).
  - `/predict` : Reçoit un `user_id` et un `isbn`, charge le modèle depuis MLflow, et retourne la note prédite (`predicted_rating`).
- **Middleware :** Ajout d'un middleware calculant le temps de traitement interne et l'ajoutant dans les headers de la réponse (`X-Process-Time`) pour le monitoring de la latence.

### 4. Conteneurisation (Docker)
- **Dockerfile API :** Création de `docker/Dockerfile.api` (basé sur `python:3.12-slim`) pour packager l'API FastAPI et ses dépendances.
- **Docker Compose :** Création de `docker-compose.yml` à la racine pour orchestrer simultanément :
  - Le serveur **MLflow** (exposé sur le port 5000).
  - L'**API FastAPI** (exposée sur le port 8000).

### 5. Script de Monitoring (`mlops/monitoring/monitor.py`)
Un script Python dédié tourne en tâche de fond pour surveiller la santé du système :
- **Healthcheck & Latence :** Interroge l'endpoint `/health` régulièrement pour s'assurer que l'API est "UP" et mesure la latence globale du réseau.
- **Latence Interne :** Fait des appels à `/predict` avec des utilisateurs aléatoires et extrait le `X-Process-Time` pour mesurer le temps de calcul brut du modèle.
- **Détection de Dérive (Data Drift) :** Calcule une moyenne glissante sur les dernières prédictions. Si la note moyenne prédite s'écarte significativement de la norme attendue du dataset (ex: < 5.0 ou > 9.5), une alerte est levée dans les logs.
- Les logs sont stockés dans `logs/api_monitoring.log`.

---

## 🚀 Comment lancer le projet complet

### 1. Générer les données d'entraînement
Depuis la racine du projet, exécutez la préparation des données :
```bash
python mlops/training/prepare_data.py
```

### 2. Démarrer MLflow et l'API (Docker Compose)
Lancez les conteneurs en arrière-plan :
```bash
docker-compose up --build -d
```
- L'interface MLflow sera accessible sur : `http://localhost:5000`
- L'API (Swagger UI) sera accessible sur : `http://localhost:8000/docs`

### 3. Entraîner le modèle
Une fois MLflow lancé, exécutez le script d'entraînement pour générer et enregistrer le modèle :
```bash
python mlops/training/train.py
```

### 4. Lancer le Monitoring
Dans un autre terminal, démarrez le script de surveillance :
```bash
python mlops/monitoring/monitor.py
```

---

## 📌 Prochaines étapes (à finaliser par l'équipe)
- **Déploiement Cloud (Komodo) :** Déployer les images Docker via l'interface Komodo de l'école.
- **CI/CD :** (Si requis) Vérifier que les GitHub Actions dans `.github/workflows` passent au vert.
- **Soutenance :** Préparer la démonstration live et les slides en intégrant les parties DataOps et MLOps de manière fluide.
