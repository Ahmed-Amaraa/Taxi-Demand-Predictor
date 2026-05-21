import mlflow
import joblib
import os
import pandas as pd
from config import Config
from datetime import datetime

class ModelService:
    """Service pour gérer les modèles (versioning, rollback)"""
    
    def __init__(self):
        self.config = Config()
        mlflow.set_tracking_uri(self.config.MLFLOW_TRACKING_URI)
    
    def list_models(self):
        """Liste tous les modèles disponibles avec versions"""
        try:
            experiment = mlflow.get_experiment_by_name(
                self.config.MLFLOW_EXPERIMENT_NAME
            )
            
            # Vérifier si l'expérience existe
            if not experiment:
                return {"models": {}}
            
            runs = mlflow.search_runs(
                experiment_ids=[experiment.experiment_id],
                order_by=["start_time DESC"]
            )
            
            # Si pas de runs, retourner vide
            if runs is None or runs.empty:
                return {"models": {}}
            
            # Grouper par modèle
            models = {}
            for _, run in runs.iterrows():
                # Utiliser la bonne syntaxe pour accéder aux colonnes pandas
                model_name = run['tags.model_type'] if 'tags.model_type' in run.index else None
                if not model_name or (isinstance(model_name, float) and pd.isna(model_name)):
                    continue
                
                model_name = str(model_name)
                if model_name not in models:
                    models[model_name] = []
                
                # Extraire les métriques de manière sécurisée
                r2_val = run['metrics.r2'] if 'metrics.r2' in run.index else None
                rmse_val = run['metrics.rmse'] if 'metrics.rmse' in run.index else None
                mae_val = run['metrics.mae'] if 'metrics.mae' in run.index else None
                
                models[model_name].append({
                    "version": len(models[model_name]) + 1,
                    "run_id": run['run_id'],
                    "metrics": {
                        "r2": float(r2_val) if pd.notna(r2_val) else None,
                        "rmse": float(rmse_val) if pd.notna(rmse_val) else None,
                        "mae": float(mae_val) if pd.notna(mae_val) else None
                    },
                    "timestamp": run['start_time'],
                    "status": run['tags.status'] if 'tags.status' in run.index else None
                })
            
            return {"models": models}
        
        except Exception as e:
            print(f"Error in list_models: {e}")
            return {"models": {}}
    
    def get_model_info(self, model_name):
        """Retourne les infos d'un modèle spécifique"""
        try:
            experiment = mlflow.get_experiment_by_name(
                self.config.MLFLOW_EXPERIMENT_NAME
            )
            
            # Vérifier si l'expérience existe
            if not experiment:
                return None
            
            filter_string = f"tags.model_type = '{model_name}'"
            runs = mlflow.search_runs(
                experiment_ids=[experiment.experiment_id],
                filter_string=filter_string,
                order_by=["start_time DESC"]
            )
            
            if runs is None or runs.empty:
                return None
            
            latest_run = runs.iloc[0]
            
            # Extraire les métriques de manière sécurisée
            r2_val = latest_run['metrics.r2'] if 'metrics.r2' in latest_run.index else None
            rmse_val = latest_run['metrics.rmse'] if 'metrics.rmse' in latest_run.index else None
            mae_val = latest_run['metrics.mae'] if 'metrics.mae' in latest_run.index else None
            
            return {
                "model_name": model_name,
                "latest_version": {
                    "run_id": latest_run['run_id'],
                    "metrics": {
                        "r2": float(r2_val) if pd.notna(r2_val) else None,
                        "rmse": float(rmse_val) if pd.notna(rmse_val) else None,
                        "mae": float(mae_val) if pd.notna(mae_val) else None
                    },
                    "params": dict((k.replace('params.', ''), v) for k, v in latest_run.items() if isinstance(k, str) and k.startswith('params.')),
                    "timestamp": latest_run['start_time']
                },
                "total_versions": len(runs)
            }
        
        except Exception as e:
            print(f"Error in get_model_info: {e}")
            return None
    
    def rollback_to_version(self, model_name, version):
        """Rollback à une version précédente"""
        try:
            experiment = mlflow.get_experiment_by_name(
                self.config.MLFLOW_EXPERIMENT_NAME
            )
            
            # Vérifier si l'expérience existe
            if not experiment:
                raise ValueError("Experiment not found")
            
            filter_string = f"tags.model_type = '{model_name}'"
            runs = mlflow.search_runs(
                experiment_ids=[experiment.experiment_id],
                filter_string=filter_string,
                order_by=["start_time DESC"]
            )
            
            if version > len(runs) or version < 1:
                raise ValueError(f"Version {version} not found")
            
            target_run = runs.iloc[version - 1]
            run_id = target_run['run_id']
            
            # Charger le modèle depuis MLflow
            model_uri = f"runs:/{run_id}/model"
            model = mlflow.sklearn.load_model(model_uri)
            
            # Sauvegarder comme version courante
            model_path = os.path.join(
                self.config.MODELS_DIR,
                f"{model_name}_current.joblib"
            )
            os.makedirs(self.config.MODELS_DIR, exist_ok=True)
            joblib.dump(model, model_path)
            
            return {
                "status": "success",
                "message": f"Rolled back {model_name} to version {version}",
                "run_id": run_id,
                "model_path": model_path,
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            print(f"Error in rollback_to_version: {e}")
            raise e