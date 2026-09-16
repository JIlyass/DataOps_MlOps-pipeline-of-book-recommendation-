from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import mlflow
import time
import os
import pandas as pd

app = FastAPI(title="Book Recommender API")

# Configuration de MLflow et du modèle
# Au démarrage de l'API, on configure l'URI et on essaie de charger le modèle.
# Si le serveur MLflow n'est pas encore prêt, cela peut échouer, d'où l'importance de Depends_on dans docker-compose.
mlflow_uri = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
mlflow.set_tracking_uri(mlflow_uri)
MODEL_URI = "models:/book-recommender-model/latest"

model = None

def load_model() -> bool:
    global model
    try:
        model = mlflow.sklearn.load_model(MODEL_URI)
        print("Modèle chargé avec succès depuis MLflow.")
        return True
    except Exception as e:
        print(f"Modèle indisponible dans MLflow : {e}")
        return False


@app.on_event("startup")
def load_model_at_startup():
    load_model()

class PredictionRequest(BaseModel):
    user_id: int
    isbn: str

class PredictionResponse(BaseModel):
    user_id: int
    isbn: str
    predicted_rating: float

# Middleware pour tracker le temps de réponse (Livrable 9 - Monitoring)
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    response.headers["X-Process-Time"] = str(duration)
    # Dans un vrai projet, on enverrait `duration` vers Prometheus ou DataDog
    return response

@app.get("/health")
def health():
    if model is None:
        load_model()
    if model is None:
        return {"status": "degraded", "message": "Model not loaded"}
    return {"status": "ok"}

@app.post("/predict", response_model=PredictionResponse)
def predict(req: PredictionRequest):
    if model is None:
        load_model()
    if model is None:
        raise HTTPException(status_code=503, detail="Modèle non disponible.")
    
    try:
        # Créer un DataFrame similaire à l'entraînement
        input_data = pd.DataFrame([{"user_id": req.user_id, "isbn": req.isbn}])
        pred = model.predict(input_data)[0]
        
        return PredictionResponse(
            user_id=req.user_id,
            isbn=req.isbn,
            predicted_rating=float(pred)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
