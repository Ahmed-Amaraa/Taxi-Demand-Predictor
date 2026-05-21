from flask import Blueprint, jsonify
from services.model_service import ModelService
from utils.helpers import ResponseHelper


models_bp = Blueprint('models', __name__)
model_service = None

def get_model_service():
    """Lazy load the model service"""
    global model_service
    if model_service is None:
        model_service = ModelService()
    return model_service

@models_bp.route('/models', methods=['GET'])
def get_models():
    """
    GET /api/models
    Liste tous les modèles disponibles avec leurs versions
    """
    try:
        service = get_model_service()
        models = service.list_models()
        return ResponseHelper.success_response(models, "Models list retrieved"), 200
    
    except Exception as e:
        return ResponseHelper.error_response(str(e), "MODELS_ERROR"), 500
    
@models_bp.route('/models/available', methods=['GET'])
def get_available_models():
    """
    GET /api/models/available
    Retourne les modèles disponibles
    """
    try:
        from utils.validators import HyperparamValidator
        validator = HyperparamValidator()
        
        available = {
            "Linear": validator.get_default_hyperparams("Linear"),
            "RF": validator.get_default_hyperparams("RF"),
            "XGB": validator.get_default_hyperparams("XGB"),
            "ADA": validator.get_default_hyperparams("ADA")
        }
        
        return ResponseHelper.success_response(available, "Available models retrieved"), 200
    
    except Exception as e:
        return ResponseHelper.error_response(str(e), "ERROR"), 500

@models_bp.route('/models/<model_name>', methods=['GET'])
def get_model_info(model_name):
    """
    GET /api/models/<model_name>
    Retourne les infos d'un modèle spécifique
    """
    try:
        service = get_model_service()
        model_info = service.get_model_info(model_name)
        if not model_info:
            return ResponseHelper.error_response(f'Model {model_name} not found', "NOT_FOUND"), 404
        return ResponseHelper.success_response(model_info, f"Model {model_name} info retrieved"), 200
    
    except Exception as e:
        return ResponseHelper.error_response(str(e), "MODELS_ERROR"), 500