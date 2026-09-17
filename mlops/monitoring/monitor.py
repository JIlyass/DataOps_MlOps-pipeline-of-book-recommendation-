import time
import httpx
import logging
import os
import random

# Configuration du logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename='logs/api_monitoring.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

API_URL = os.getenv("API_URL", "http://localhost:5102")

def check_api_health():
    """Vérifie si l'API est disponible et enregistre le temps de réponse."""
    try:
        # On appelle le endpoint /health
        start_time = time.time()
        response = httpx.get(f"{API_URL}/health", timeout=5.0)
        end_time = time.time()
        
        latency_ms = (end_time - start_time) * 1000
        
        if response.status_code == 200:
            status = response.json().get("status", "unknown")
            msg = f"API OK | Statut: {status} | Temps de réponse global: {latency_ms:.2f} ms"
            print(f"[OK] {msg}")
            logging.info(msg)
        else:
            msg = f"API DEGRADED | Code HTTP: {response.status_code}"
            print(f"[WARN] {msg}")
            logging.warning(msg)
            
    except httpx.RequestError as e:
        msg = f"API DOWN | Impossible de se connecter: {e}"
        print(f"[FAIL] {msg}")
        logging.error(msg)

def test_prediction_latency(user_id, isbn, recent_predictions):
    """Envoie une requête de prédiction pour mesurer le 'X-Process-Time' interne."""
    try:
        payload = {"user_id": user_id, "isbn": isbn}
        response = httpx.post(f"{API_URL}/predict", json=payload, timeout=5.0)
        
        if response.status_code == 200:
            # L'API FastAPI renvoie le temps de calcul interne dans ce header (notre middleware)
            process_time = response.headers.get("x-process-time")
            if process_time:
                process_time_ms = float(process_time) * 1000
                msg = f"PREDICTION OK | Temps de calcul interne (FastAPI): {process_time_ms:.2f} ms"
                print(f"[TIME] {msg}")
                logging.info(msg)
                
            # --- SUIVI DE DÉRIVE SIMPLE (DATA DRIFT) ---
            predicted_rating = response.json().get("predicted_rating", 0)
            recent_predictions.append(predicted_rating)
            
            # On garde seulement les 10 dernières prédictions
            if len(recent_predictions) > 10:
                recent_predictions.pop(0)
                
            # Calcul de la moyenne glissante
            if len(recent_predictions) >= 5:
                avg_rating = sum(recent_predictions) / len(recent_predictions)
                
                # Baseline attendue : Dans le dataset Book-Crossing, la moyenne tourne autour de 7.5
                # Si notre modèle se met à prédire des moyennes extrêmes, on alerte !
                if avg_rating < 5.0 or avg_rating > 9.5:
                    drift_msg = f"ALERTE DÉRIVE (DRIFT) | Moyenne glissante anormale : {avg_rating:.2f}/10"
                    print(f"[DRIFT-WARN] {drift_msg}")
                    logging.warning(drift_msg)
                else:
                    drift_msg = f"DÉRIVE OK | Moyenne glissante stable : {avg_rating:.2f}/10"
                    print(f"[DRIFT-OK] {drift_msg}")
                    logging.info(drift_msg)
            # -------------------------------------------
            
    except Exception as e:
        pass # Déjà loggé par check_api_health si l'API est down

if __name__ == "__main__":
    print("Démarrage du monitoring de l'API (Appuyez sur Ctrl+C pour arrêter)...")
    print(f"Les logs sont sauvegardés dans 'logs/api_monitoring.log'\n")
    
    # Historique pour le calcul de la dérive (Drift)
    recent_predictions = []
    
    try:
        while True:
            check_api_health()
            
            # On simule un utilisateur aléatoire pour faire varier la prédiction
            test_user_id = random.choice([123, 276744, 276721, 276723, 278418])
            test_isbn = random.choice(["0123456789", "038550120X", "034545104X", "0060930535"])
            test_prediction_latency(test_user_id, test_isbn, recent_predictions)
            
            print("-" * 50)
            time.sleep(5)  # Pause de 5 secondes entre chaque vérification
    except KeyboardInterrupt:
        print("\nArrêt du monitoring.")
