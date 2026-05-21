from flask import Blueprint, request, jsonify
from services.prediction_service import PredictionService
from utils.helpers import ResponseHelper

prediction_bp = Blueprint('prediction', __name__)
prediction_service = None

def get_prediction_service():
    """Lazy load the prediction service"""
    global prediction_service
    if prediction_service is None:
        prediction_service = PredictionService()
    return prediction_service

@prediction_bp.route('/best-models', methods=['GET'])
def get_best_models():
    """
    GET /api/best-models
    Retourne les meilleurs modèles pour chaque type
    """
    try:
        service = get_prediction_service()
        models = service.get_best_models()
        if not models:
            return ResponseHelper.error_response("No models found", "NO_MODELS"), 404
        
        return ResponseHelper.success_response(models, "Best models retrieved"), 200
    
    except Exception as e:
        return ResponseHelper.error_response(str(e), "ERROR"), 500

@prediction_bp.route('/predict', methods=['POST'])
def predict():
    """
    POST /api/predict
    Body: {
        "model_type": "Linear" | "RF" | "XGB",
        "features": {
            "hour": 10,
            "day": 3,
            "month": 4,
            "lag_1": 150,
            "lag_24": 145,
            "rolling_mean_3": 148,
            "zone": 5
        }
    }
    """
    try:
        data = request.get_json()
        model_type = data.get('model_type')
        features = data.get('features', {})
        
        if not model_type:
            return ResponseHelper.error_response("model_type is required", "INVALID_INPUT"), 400
        
        if not features:
            return ResponseHelper.error_response("features are required", "INVALID_INPUT"), 400
        
        service = get_prediction_service()
        result = service.predict(model_type, features)
        return ResponseHelper.success_response(result, "Prediction successful"), 200
    
    except ValueError as e:
        return ResponseHelper.error_response(str(e), "INVALID_MODEL"), 400
    except Exception as e:
        return ResponseHelper.error_response(str(e), "PREDICTION_ERROR"), 500
