from flask import Blueprint, request, jsonify
from services.training_service import TrainingService
from services.visualization_service import VisualizationService
from utils.validators import HyperparamValidator
from utils.helpers import ResponseHelper
import numpy as np

train_bp = Blueprint('train', __name__)
training_service = None
visualization_service = None
validator = HyperparamValidator()

def get_training_service():
    """Lazy load the training service"""
    global training_service
    if training_service is None:
        training_service = TrainingService()
    return training_service

def get_visualization_service():
    """Lazy load the visualization service"""
    global visualization_service
    if visualization_service is None:
        visualization_service = VisualizationService()
    return visualization_service

@train_bp.route('/train', methods=['POST'])
def train_model():
    """
    POST /api/train
    Body: {
        "model_name": "XGB",
        "hyperparams": {
            "n_estimators": 300,
            "max_depth": 6,
            "learning_rate": 0.01
        }
    }
    """
    try:
        data = request.get_json()
        model_name = data.get('model_name')
        hyperparams = data.get('hyperparams', {})
        
        # Valider le modèle
        is_valid, msg = validator.validate_model_name(model_name)
        if not is_valid:
            return ResponseHelper.error_response(msg, "INVALID_MODEL"), 400
        
        # Valider les hyperparamètres
        is_valid, msg = validator.validate_hyperparams(model_name, hyperparams)
        if not is_valid:
            return ResponseHelper.error_response(msg, "INVALID_HYPERPARAMS"), 400
        
        # Utiliser les hyperparamètres par défaut si vides
        if not hyperparams:
            hyperparams = validator.get_default_hyperparams(model_name)
        
        # Lancer l'entraînement
        train_srv = get_training_service()
        result = train_srv.train(model_name, hyperparams)
        
        # Récupérer y_test et y_pred
        y_test = np.array(result['y_test'])
        y_pred = np.array(result['y_pred'])
        run_id = result['run_id']
        
        # Générer les visualisations
        viz_srv = get_visualization_service()
        visualizations = []
        
        try:
            visualizations.append(
                viz_srv.plot_predictions_vs_actual(
                    y_test, y_pred, model_name, run_id
                )
            )
        except Exception as e:
            print(f"Erreur predictions_vs_actual: {e}")
        
        try:
            visualizations.append(
                viz_srv.plot_residuals(
                    y_test, y_pred, model_name, run_id
                )
            )
        except Exception as e:
            print(f"Erreur residuals: {e}")
        
        try:
            visualizations.append(
                viz_srv.plot_error_distribution(
                    y_test, y_pred, model_name, run_id
                )
            )
        except Exception as e:
            print(f"Erreur error_distribution: {e}")
        
        try:
            visualizations.append(
                viz_srv.export_results_to_csv(
                    y_test, y_pred, model_name, run_id
                )
            )
        except Exception as e:
            print(f"Erreur CSV export: {e}")
        
        try:
            visualizations.append(
                viz_srv.export_figure_as_png(
                    y_test, y_pred, model_name, run_id
                )
            )
        except Exception as e:
            print(f"Erreur PNG export: {e}")
        
        # Ajouter la visualisation des importances de features si disponible
        if result.get('feature_importances'):
            try:
                viz = viz_srv.plot_feature_importances(
                    result['feature_importances'], model_name, run_id
                )
                if viz:
                    visualizations.append(viz)
            except Exception as e:
                print(f"Erreur feature_importances: {e}")
        
        result['visualizations'] = visualizations
        
        # Supprimer les données brutes
        del result['y_test']
        del result['y_pred']
        
        return ResponseHelper.success_response(result, "Model trained successfully"), 200
    
    except Exception as e:
        return ResponseHelper.error_response(str(e), "TRAINING_ERROR"), 500

@train_bp.route('/models/available', methods=['GET'])
def get_available_models():
    """
    GET /api/models/available
    Retourne les modèles disponibles et leurs hyperparamètres par défaut
    """
    try:
        available_models = {
            "Linear": {
                "name": "Linear Regression",
                "description": "Régression linéaire simple",
                "hyperparams": validator.get_default_hyperparams("Linear")
            },
            "RF": {
                "name": "Random Forest",
                "description": "Ensemble de forêts aléatoires",
                "hyperparams": validator.get_default_hyperparams("RF"),
                "limits": validator.LIMITS["RF"]
            },
            "XGB": {
                "name": "XGBoost",
                "description": "Gradient Boosting optimisé",
                "hyperparams": validator.get_default_hyperparams("XGB"),
                "limits": validator.LIMITS["XGB"]
            },
            "ADA": {
                "name": "AdaBoost",
                "description": "Adaptive Boosting Regressor",
                "hyperparams": validator.get_default_hyperparams("ADA"),
                "limits": validator.LIMITS["ADA"]
            }
        }
        
        return ResponseHelper.success_response(
            available_models,
            "Available models retrieved"
        ), 200
    
    except Exception as e:
        return ResponseHelper.error_response(str(e), "ERROR"), 500