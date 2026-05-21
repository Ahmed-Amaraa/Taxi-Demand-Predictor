import pandas as pd
import numpy as np
import mlflow
import mlflow.sklearn
import mlflow.xgboost
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, AdaBoostRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import xgboost as xgb
import joblib
from datetime import datetime
from config import Config
import os

class TrainingService:
    """Service pour l'entraînement des modèles avec MLflow"""
    
    def __init__(self):
        self.config = Config()
        mlflow.set_tracking_uri(self.config.MLFLOW_TRACKING_URI)
        mlflow.set_experiment(self.config.MLFLOW_EXPERIMENT_NAME)
        self.dataset_version = self._get_dataset_version()
    
    def _get_dataset_version(self):
        """Récupère la version du dataset"""
        dataset_path = self.config.DATASET_PATH
        if os.path.exists(dataset_path):
            timestamp = os.path.getmtime(dataset_path)
            return datetime.fromtimestamp(timestamp).isoformat()
        return "unknown"
    
    def train(self, model_name, hyperparams):
        """
        Entraîne un modèle avec MLflow tracking
        
        Args:
            model_name: "Linear", "RF", "XGB", "ADA"
            hyperparams: dict des hyperparamètres
        
        Returns:
            dict avec résultats d'entraînement + données pour visualisation
        """
        try:
            # Charger le dataset
            df = pd.read_parquet(self.config.DATASET_PATH)
            df = df.sort_values('pickup_hour')
            df.drop(columns=['pickup_hour'], inplace=True)
            
            # Préparer les données
            X = df.drop(columns=['demand'])
            y = df['demand']
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Créer le modèle
            model = self._create_model(model_name, hyperparams)
            
            # MLflow run
            with mlflow.start_run(run_name=f"{model_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"):
                
                # Entraîner
                model.fit(X_train, y_train)
                preds = model.predict(X_test)
                
                # Calculer les métriques
                rmse = np.sqrt(mean_squared_error(y_test, preds))
                mae = mean_absolute_error(y_test, preds)
                r2 = r2_score(y_test, preds)
                
                # Log des paramètres
                mlflow.log_param("model_name", model_name)
                mlflow.log_params(hyperparams)
                mlflow.log_param("dataset_version", self.dataset_version)
                
                # Log des métriques
                mlflow.log_metric("rmse", rmse)
                mlflow.log_metric("mae", mae)
                mlflow.log_metric("r2", r2)
                
                # Log du modèle
                mlflow.sklearn.log_model(model, artifact_path="model")
                
                # Log de tags
                mlflow.set_tag("model_type", model_name)
                mlflow.set_tag("status", "completed")
                
                # Sauvegarder localement
                model_path = os.path.join(
                    self.config.MODELS_DIR, 
                    f"{model_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.joblib"
                )
                os.makedirs(self.config.MODELS_DIR, exist_ok=True)
                joblib.dump(model, model_path)
                
                run_id = mlflow.active_run().info.run_id
                
                # Extraire les feature importances
                feature_importances = None
                if hasattr(model, 'feature_importances_'):
                    importances = model.feature_importances_
                    feature_importances = {
                        "features": X.columns.tolist(),
                        "importances": importances.tolist()
                    }
                
                return {
                    "status": "success",
                    "model_name": model_name,
                    "run_id": run_id,
                    "metrics": {
                        "rmse": float(rmse),
                        "mae": float(mae),
                        "r2": float(r2)
                    },
                    "feature_importances": feature_importances,
                    "model_path": model_path,
                    "dataset_version": self.dataset_version,
                    "timestamp": datetime.now().isoformat(),
                    # Ajouter les données pour visualisation
                    "y_test": y_test.tolist(),
                    "y_pred": preds.tolist(),
                    "test_size": len(y_test)
                }
        
        except Exception as e:
            mlflow.set_tag("status", "failed")
            raise e
    
    def _create_model(self, model_name, hyperparams):
        """Crée une instance du modèle avec hyperparamètres"""
        if model_name == "Linear":
            return LinearRegression(**hyperparams)
        elif model_name == "RF":
            return RandomForestRegressor(**hyperparams)
        elif model_name == "XGB":
            return xgb.XGBRegressor(**hyperparams)
        elif model_name == "ADA":
            return AdaBoostRegressor(**hyperparams)
        else:
            raise ValueError(f"Model {model_name} not supported")