from flask import Blueprint, jsonify
from services.metrics_service import MetricsService
from services.visualization_service import VisualizationService
from utils.helpers import ResponseHelper
from datetime import datetime

results_bp = Blueprint('results', __name__)
metrics_service = None
visualization_service = None

def get_metrics_service():
    """Lazy load the metrics service"""
    global metrics_service
    if metrics_service is None:
        metrics_service = MetricsService()
    return metrics_service

def get_visualization_service():
    """Lazy load the visualization service"""
    global visualization_service
    if visualization_service is None:
        visualization_service = VisualizationService()
    return visualization_service

@results_bp.route('/results', methods=['GET'])
def get_results():
    """
    GET /api/results
    Retourne toutes les métriques et visualisations
    """
    try:
        service = get_metrics_service()
        results = service.get_all_results()
        results['timestamp'] = datetime.now().isoformat()
        return ResponseHelper.success_response(results, "Results retrieved successfully"), 200
    
    except Exception as e:
        return ResponseHelper.error_response(str(e), "RESULTS_ERROR"), 500

@results_bp.route('/results/compare/all', methods=['GET'])
def compare_all_models():
    """
    GET /api/results/compare/all
    Génère une comparaison visuelle de tous les modèles
    """
    try:
        metrics_srv = get_metrics_service()
        viz_srv = get_visualization_service()
        
        all_results = metrics_srv.get_all_results()
        runs = all_results['runs']
        
        if not runs:
            return ResponseHelper.error_response('No runs found', "NOT_FOUND"), 404
        
        # Visualisations comparatives
        comparison_chart = viz_srv.plot_models_comparison(runs)
        r2_chart = viz_srv.plot_r2_comparison(runs)
        
        best_model_info = metrics_srv.compare_models()
        
        comparison_data = {
            "total_runs": len(runs),
            "comparison": runs,
            "visualizations": [v for v in [comparison_chart, r2_chart] if v is not None],
            "best_model": best_model_info
        }
        
        return ResponseHelper.success_response(comparison_data, "Models comparison retrieved"), 200
    
    except Exception as e:
        return ResponseHelper.error_response(str(e), "COMPARISON_ERROR"), 500

@results_bp.route('/results/<model_name>', methods=['GET'])
def get_model_results(model_name):
    """
    GET /api/results/<model_name>
    Retourne les résultats d'un modèle spécifique
    """
    try:
        service = get_metrics_service()
        results = service.get_results_by_model(model_name)
        if not results or not results.get('runs'):
            return ResponseHelper.error_response(f'No results for model {model_name}', "NOT_FOUND"), 404
        return ResponseHelper.success_response(results, f"Results for {model_name} retrieved"), 200
    
    except Exception as e:
        return ResponseHelper.error_response(str(e), "RESULTS_ERROR"), 500