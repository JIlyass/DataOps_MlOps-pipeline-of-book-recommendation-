# Handover - Partie Déploiement, CI/CD et Infrastructure du projet Book Recommender

## 1. Contexte de ma contribution

Ma contribution porte sur la partie infrastructure et automatisation du projet : mise en place du déploiement des services, configuration des conteneurs, orchestration Dagster, intégration MLflow/API, liaison GitHub + Komodo, et mise en place de la validation continue avec redéploiement automatique.

Je ne détaille pas ici le travail des autres parties du projet (modélisation, préparation des données, dbt, etc.), mais uniquement ce que j’ai mis en place au niveau système, déploiement et automatisation.

---

## 2. Objectif de la partie réalisée

L’objectif était de rendre le projet exploitable en environnement réel et reproductible, avec :

- des services conteneurisés,
- un environnement de déploiement cohérent,
- un orchestration stable avec Dagster,
- un suivi des expérimentations avec MLflow,
- une API FastAPI prête à servir les prédictions,
- une validation automatique du code via GitHub Actions,
- un déclenchement automatique de redéploiement sur Komodo.

---

## 3. Ce que j’ai configuré

### 3.1. Déploiement de l’environnement applicatif

J’ai configuré le fichier [docker-compose.yml](docker-compose.yml) pour lancer simultanément les services suivants :

- MLflow
  - service principal de tracking et de stockage des modèles,
  - exposé sur le port 5101,
  - stockage des artefacts dans les volumes MLflow,
  - healthcheck pour vérifier sa disponibilité.

- Dagster webserver
  - service web de Dagster,
  - exposé sur le port 5103,
  - point d’entrée visuel pour lancer et surveiller les jobs,
  - configuré avec le module book_pipeline.definitions.

- Dagster daemon
  - service de fond chargé d’exécuter les jobs en arrière-plan,
  - utilisé pour les tâches planifiées et non interactives,
  - fonctionnel en mode daemon avec le même environnement que le webserver.

- API FastAPI
  - service de prédiction,
  - exposé sur le port 5102,
  - connecté à MLflow pour charger le modèle en runtime,
  - fonctionnel pour répondre sur /health et /predict.

Cela permet d’avoir un système cohérent et exécutable avec une seule commande :

```bash
docker compose up --build -d
```

---

### 3.2. Gestion des volumes et persistance

J’ai pris en compte la nécessité de conserver les données entre les redéploiements. Les volumes principaux sont :

- [data](data)
- [mlflow_data](mlflow_data)
- [mlflow_db](mlflow_db)
- [dagster_home](dagster_home)

Ces volumes permettent de conserver :

- les données brutes et exploitées,
- les artefacts MLflow,
- la base MLflow,
- l’historique Dagster et l’état de l’orchestration.

C’est important pour éviter de perdre les résultats et les modèles lors d’un nouveau déploiement ou d’un redémarrage de conteneur.

---

### 3.3. Configuration de Dagster

J’ai mis en place la configuration du webserver et du daemon Dagster dans le compose.

#### Points importants
- DAGSTER_HOME est défini dans l’environnement du conteneur.
- Les volumes partagés permettent au webserver et au daemon de fonctionner sur le même espace Dagster.
- Le webserver est branché sur le module :

```python
book_pipeline.definitions
```

- Le daemon est lancé avec la même configuration pour exécuter les jobs planifiés ou déclenchés.

Le fichier [dataops/dagster_project/book_pipeline/book_pipeline/definitions.py](dataops/dagster_project/book_pipeline/book_pipeline/definitions.py) est donc intégré au système de production et peut être exposé via l’interface Dagster sur le port 5103.

J’ai aussi configuré le schedule Dagster pour un déclenchement automatique à 02:00 UTC.

---

## 4. Intégration MLflow / API / modèle

J’ai configuré les services pour que le système soit cohérent entre :

- l’API FastAPI,
- le tracking MLflow,
- le modèle enregistré,
- les jobs Dagster.

### Points de raccordement
- L’API est démarrée avec une variable d’environnement :

```env
MLFLOW_TRACKING_URI=http://mlflow:5000
```

- Au démarrage, l’API charge le modèle depuis le registre MLflow.
- L’URL du modèle est configurée pour utiliser la version latest :

```python
models:/book-recommender-model/latest
```

- Les conteneurs de l’API et de MLflow sont liés par le réseau Docker du compose.

Ce point est important car il évite d’avoir un service API “seul” sans modèle accessible ou sans tracking centralisé.

---

## 5. Déploiement sur Komodo

J’ai préparé le projet pour son déploiement sur Komodo en m’assurant que le stack soit compatible avec l’environnement cible.

Les éléments clés mis en place sont :

- utilisation du fichier [docker-compose.yml](docker-compose.yml) comme point d’entrée du stack,
- présence des services principaux dans le même fichier,
- volume persistants pour éviter la perte des données et du dépôt Dagster/MLflow,
- configuration du premier lancement avec les conteneurs dédiés.

Le document [KOMODO_DEPLOYMENT.md](KOMODO_DEPLOYMENT.md) décrit la procédure utilisée pour :

- lancer le stack Komodo,
- vérifier les services,
- démarrer la première exécution Dagster,
- vérifier le modèle dans MLflow,
- valider la disponibilité de l’API.

### Bonnes pratiques appliquées
- les données persistantes sont conservées entre les redéploiements,
- le stack est conçu pour être relancé sans réinitialiser la base MLflow ou la base DuckDB,
- le webserver et le daemon Dagster sont traités comme des services distincts mais liés.

---

## 6. GitHub Actions et validation continue

J’ai configuré la pipeline CI/CD dans [.github/workflows/ci-cd.yml](.github/workflows/ci-cd.yml).

### Workflow mis en place

La pipeline comprend plusieurs étapes :

1. checkout du dépôt,
2. installation des dépendances Python,
3. validation du code par compilation Python,
4. validation du fichier docker-compose,
5. build des images Docker pour les services DataOps et API,
6. déclenchement de webhook Komodo si la branche est main.

### Composant clé

Le secret GitHub suivant est attendu et configuré pour le déploiement automatique :

```text
KOMODO_DEPLOY_WEBHOOK_URL
```

Cela permet de faire fonctionner le flux suivant :

- push vers main,
- validation du code,
- construction des images,
- déclenchement de Komodo,
- redéploiement automatique du stack.

---

## 7. Flux de redéploiement automatique

J’ai mis en place le flux de déploiement suivant :

- le dépôt GitHub reçoit un push sur main,
- le workflow GitHub Actions se lance,
- les dépendances sont installées,
- le code est compilé,
- le fichier compose est validé,
- les images Docker sont construites,
- si tout est OK, le webhook Komodo est appelé,
- le stack est redéployé automatiquement.

Ce flux est important parce qu’il permet de passer d’un environnement de développement à un environnement de production plus fiable, sans exécution manuelle à chaque modification.

---

## 8. Ce que j’ai réellement réalisé

### En résumé
J’ai mis en place la couche d’infrastructure opérationnelle du projet :

- configuration Docker Compose du système complet,
- gestion de plusieurs services dans le même stack,
- mise en place des conteneurs webserver et daemon Dagster,
- intégration de MLflow et de l’API dans le même environnement,
- configuration du stockage persistant,
- préparation du déploiement Komodo,
- setup du workflow GitHub Actions pour validation + redéploiement automatique.

### Ce qui est vraiment central dans mon travail
- le conteneur Dagster webserver,
- le conteneur Dagster daemon,
- le service MLflow,
- le service API,
- le fichier compose final,
- le webhook GitHub → Komodo,
- la validation continue du code.

---

## 9. Points de vigilance et maintenance

Les éléments importants à surveiller lors d’un redéploiement ou d’une reprise du projet sont :

- vérifier que les volumes persistants sont bien présents,
- vérifier que les services Docker sont bien UP,
- vérifier que MLflow répond sur son endpoint de santé,
- vérifier que Dagster est bien accessible via le webserver,
- vérifier que l’API /health répond correctement,
- vérifier que le modèle est bien présent dans MLflow,
- vérifier que le secret KOMODO_DEPLOY_WEBHOOK_URL est bien configuré,
- surveiller les logs de Dagster et de l’API en cas de redémarrage.

---

## 10. État final de ma partie

Ma partie est fonctionnelle et prête pour l’exploitation durable du projet. Le système est désormais organisé autour de conteneurs Docker, d’une orchestration Dagster, d’un tracking MLflow, d’une API de service, et d’un pipeline de déploiement automatisé via GitHub Actions et Komodo.

Le point clé est que le projet n’est plus seulement un prototype de démonstration : il a été transformé en une structure plus proche d’un environnement de production avec validation et redéploiement automatique.

---

## 11. Fichiers utiles pour la reprise

- [docker-compose.yml](docker-compose.yml)
- [KOMODO_DEPLOYMENT.md](KOMODO_DEPLOYMENT.md)
- [.github/workflows/ci-cd.yml](.github/workflows/ci-cd.yml)
- [dataops/dagster_project/book_pipeline/book_pipeline/definitions.py](dataops/dagster_project/book_pipeline/book_pipeline/definitions.py)
- [mlops/api/main.py](mlops/api/main.py)
- [mlops/monitoring/monitor.py](mlops/monitoring/monitor.py)

Ce document sert de support de transmission pour expliquer précisément ce que j’ai mis en place dans la partie infrastructure et automatisation du projet.
