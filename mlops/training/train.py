import mlflow
import mlflow.sklearn
from sklearn.preprocessing import OrdinalEncoder
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error
import pandas as pd
import numpy as np
import os

def train_model():
    print("Démarrage de l'entraînement MLOps (avec scikit-learn)...")
    
    mlflow.set_tracking_uri("http://localhost:5101")
    mlflow.set_experiment("book-recommender-sklearn-proxy")
    
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    train_path = os.path.join(data_dir, "train.csv")
    test_path = os.path.join(data_dir, "test.csv")
    
    if not os.path.exists(train_path) or not os.path.exists(test_path):
        raise FileNotFoundError("Exécutez prepare_data.py d'abord.")
        
    print("Chargement des données...")
    train_df = pd.read_csv(train_path)
    test_df = pd.read_csv(test_path)
    
    X_train = train_df[["user_id", "isbn"]]
    y_train = train_df["book_rating"]
    X_test = test_df[["user_id", "isbn"]]
    y_test = test_df["book_rating"]
    
    print("Lancement de l'entraînement...")
    with mlflow.start_run(run_name="sklearn_baseline"):
        # Modèle de base scikit-learn (Ridge Regression avec encodage)
        params = {"alpha": 1.0}
        mlflow.log_params(params)
    
        model = Pipeline([
            ("encoder", OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1)),
            ("regressor", Ridge(**params))
        ])
        
        model.fit(X_train, y_train)
    
        print("Évaluation du modèle...")
        predictions = model.predict(X_test)
        rmse = float(np.sqrt(mean_squared_error(y_test, predictions)))
        mlflow.log_metric("rmse", rmse)
        
        print("Sauvegarde du modèle dans MLflow...")
        mlflow.sklearn.log_model(model, "model", serialization_format="cloudpickle", registered_model_name="book-recommender-model")
    
    print(f"Modèle entraîné et enregistré avec succès ! RMSE = {rmse:.4f}")

if __name__ == "__main__":
    train_model()
