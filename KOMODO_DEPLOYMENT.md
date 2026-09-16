# Déploiement Komodo

## Pré-requis

- Le dépôt GitHub contient la branche `main` à jour.
- Komodo peut accéder au dépôt GitHub et possède Docker Compose.
- Le serveur Komodo dispose d'un espace persistant suffisant pour les CSV,
  DuckDB, MLflow et l'historique Dagster.

## Configuration du stack

Créer un stack Komodo depuis ce dépôt et utiliser le fichier :

```text
docker-compose.yml
```

Lancer le stack avec :

```bash
docker compose up --build -d
```

Les services sont :

- `api` : port `5102`
- `mlflow` : port `5101`
- `dagster-webserver` : port `3000`
- `dagster-daemon` : service interne

Les répertoires suivants doivent rester persistants entre les redéploiements :

```text
data/
mlflow_data/
mlflow_db/
dagster_home/
```

## Premier lancement

Si le stack reste en `restarting` avec l'erreur `alembic_version has more than
one head present`, le Compose utilise le nouveau dossier `dagster_home_v2` et
recrée automatiquement une instance Dagster propre au prochain redéploiement.
L'ancien dossier `dagster_home` est conservé et aucune commande serveur n'est
nécessaire.

```bash
docker compose up --build -d dagster-webserver dagster-daemon
```

Cette opération ne supprime ni DuckDB, ni MLflow, ni le modèle enregistré.

1. Vérifier que les quatre conteneurs sont `Up`.
2. Ouvrir Dagster sur le port `3000`.
3. Lancer une première exécution de `book_pipeline_job`.
4. Vérifier dans MLflow que `book-recommender-model` est enregistré.
5. Vérifier `GET /health` sur l'API.

Le schedule est configuré automatiquement à `02:00 UTC` et activé par défaut.

## Déploiement automatique depuis GitHub

Créer dans GitHub Actions le secret :

```text
KOMODO_DEPLOY_WEBHOOK_URL
```

Sa valeur doit être le webhook de déploiement du stack Komodo. Chaque push sur
`main` valide le code, construit les images et déclenche ensuite Komodo.