import pandas as pd
import numpy as np
import mlflow
import joblib
from config import Config
from pathlib import Path

class PredictionService:
    """Service pour les prédictions avec les meilleurs modèles"""
    
    # Normalization constants (from dataset stats)
    LAG_24_MIN = 1.0
    LAG_24_MAX = 131.0
    GLOBAL_LAG_24_MIN = 1.0
    GLOBAL_LAG_24_MAX = 915.0
    
    def __init__(self):
        self.config = Config()
        mlflow.set_tracking_uri(self.config.MLFLOW_TRACKING_URI)
    
    def get_best_models(self):
        """
        Récupère les meilleurs modèles pour chaque type (Linear, RF, XGB, ADA)
        Retourne un dict avec les meilleurs modèles et leurs métriques
        """
        try:
            experiment = mlflow.get_experiment_by_name(
                self.config.MLFLOW_EXPERIMENT_NAME
            )
            
            if not experiment:
                return None
            
            best_models = {}
            model_types = ["Linear", "RF", "XGB", "ADA"]
            
            for model_type in model_types:
                filter_string = f"tags.model_type = '{model_type}'"
                runs = mlflow.search_runs(
                    experiment_ids=[experiment.experiment_id],
                    filter_string=filter_string,
                    order_by=["metrics.r2 DESC"]
                )
                
                if runs is not None and not runs.empty:
                    best_run = runs.iloc[0]
                    
                    best_models[model_type] = {
                        "run_id": best_run['run_id'],
                        "metrics": {
                            "r2": float(best_run['metrics.r2']) if 'metrics.r2' in best_run.index else None,
                            "rmse": float(best_run['metrics.rmse']) if 'metrics.rmse' in best_run.index else None,
                            "mae": float(best_run['metrics.mae']) if 'metrics.mae' in best_run.index else None
                        },
                        "timestamp": best_run['start_time']
                    }
            
            return best_models
        
        except Exception as e:
            print(f"Error in get_best_models: {e}")
            return None
    
    def _normalize_value(self, value, min_val, max_val):
        """Normalize value using min-max normalization"""
        return (value - min_val) / (max_val - min_val)
    
    def predict(self, model_type, features):
        """
        Fait une prédiction avec le meilleur modèle du type spécifié
        
        Args:
            model_type: "Linear", "RF", "XGB", ou "ADA"
            features: dict avec les features:
                - hour: heure du jour (0-23)
                - day: jour de la semaine (0-6)
                - month: mois (1-12)
                - zone: zone (0-29)
                - lag_1: demande (heure-1)
                - lag_24: demande (heure-24, zone)
                - global_lag_24: demande (heure-24, global)
        
        Returns:
            dict avec la prédiction et les informations du modèle
        """
        try:
            # Valider le type de modèle
            if model_type not in ["Linear", "RF", "XGB", "ADA"]:
                raise ValueError(f"Invalid model type: {model_type}")
            
            # Récupérer le meilleur modèle
            experiment = mlflow.get_experiment_by_name(
                self.config.MLFLOW_EXPERIMENT_NAME
            )
            
            if not experiment:
                raise Exception("No experiment found")
            
            filter_string = f"tags.model_type = '{model_type}'"
            runs = mlflow.search_runs(
                experiment_ids=[experiment.experiment_id],
                filter_string=filter_string,
                order_by=["metrics.r2 DESC"]
            )
            
            if runs is None or runs.empty:
                raise Exception(f"No models found for type {model_type}")
            
            best_run = runs.iloc[0]
            run_id = best_run['run_id']
            
            # Charger le modèle
            model_uri = f"runs:/{run_id}/model"
            model = mlflow.sklearn.load_model(model_uri)
            
            # Extraire les valeurs de base
            hour = features.get('hour', 0)
            day = features.get('day', 0)
            month = features.get('month', 1)
            zone = features.get('zone', 0)
            lag_1 = features.get('lag_1', 0)
            lag_24 = features.get('lag_24', 0)
            global_lag_24 = features.get('global_lag_24', 0)
            
            # Calculer les features normalisées
            lag_24_norm = self._normalize_value(lag_24, self.LAG_24_MIN, self.LAG_24_MAX)
            global_lag_24_norm = self._normalize_value(global_lag_24, self.GLOBAL_LAG_24_MIN, self.GLOBAL_LAG_24_MAX)
            diff = lag_24 - global_lag_24
            
            # Préparer les données pour la prédiction
            # Ordre des features du modèle: zone, hour, day, month, lag_1, lag_24, global_lag_24, lag_24_norm, global_lag_24_norm, diff
            X = pd.DataFrame([{
                'zone': zone,
                'hour': hour,
                'day': day,
                'month': month,
                'lag_1': lag_1,
                'lag_24': lag_24,
                'global_lag_24': global_lag_24,
                'lag_24_norm': lag_24_norm,
                'global_lag_24_norm': global_lag_24_norm,
                'diff': diff
            }])
            
            # Faire la prédiction
            prediction = model.predict(X)[0]
            
            # Récupérer les métriques du modèle
            metrics = {
                "r2": float(best_run['metrics.r2']) if 'metrics.r2' in best_run.index else None,
                "rmse": float(best_run['metrics.rmse']) if 'metrics.rmse' in best_run.index else None,
                "mae": float(best_run['metrics.mae']) if 'metrics.mae' in best_run.index else None
            }
            
            return {
                "prediction": float(prediction),
                "model_type": model_type,
                "run_id": run_id,
                "metrics": metrics,
                "input_features": {
                    "zone": zone,
                    "hour": hour,
                    "day": day,
                    "month": month,
                    "lag_1": lag_1,
                    "lag_24": lag_24,
                    "global_lag_24": global_lag_24,
                    "lag_24_norm": round(lag_24_norm, 4),
                    "global_lag_24_norm": round(global_lag_24_norm, 4),
                    "diff": diff
                }
            }
        
        except Exception as e:
            raise e

