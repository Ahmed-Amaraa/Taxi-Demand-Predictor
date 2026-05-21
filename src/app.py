from flask import Flask, send_file, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import sys
from pathlib import Path

# Ensure src directory is in Python path
sys.path.insert(0, str(Path(__file__).parent))

from config import config

load_dotenv()

def create_app(config_name=None):
    """Factory pour créer l'application Flask"""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Activer CORS
    CORS(app)
    
    # Importer et enregistrer les blueprints
    from routes.train import train_bp
    from routes.results import results_bp
    from routes.models import models_bp
    from routes.prediction import prediction_bp
    
    app.register_blueprint(train_bp, url_prefix='/api')
    app.register_blueprint(results_bp, url_prefix='/api')
    app.register_blueprint(models_bp, url_prefix='/api')
    app.register_blueprint(prediction_bp, url_prefix='/api')
    
    # Route de santé
    @app.route('/health', methods=['GET'])
    def health():
        return {'status': 'ok'}, 200
    
    # Servir les fichiers de visualisation
    @app.route('/api/visualizations/<path:filename>', methods=['GET'])
    def serve_visualization(filename):
        """Serve visualization files (HTML, PNG, CSV, etc)"""
        try:
            from config import Config
            viz_dir = Path(Config.RESULTS_DIR) / "visualizations"
            file_path = viz_dir / filename
            
            # Vérifier que le chemin est dans le répertoire autorisé (sécurité)
            if not str(file_path).startswith(str(viz_dir)):
                return jsonify({"error": "Path traversal not allowed"}), 403
            
            if not file_path.exists():
                return jsonify({"error": f"File not found: {filename}"}), 404
            
            # Déterminer le MIME type
            mime_type = 'text/html'
            if filename.endswith('.png'):
                mime_type = 'image/png'
            elif filename.endswith('.csv'):
                mime_type = 'text/csv'
            elif filename.endswith('.html'):
                mime_type = 'text/html'
            
            return send_file(str(file_path), mimetype=mime_type)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.getenv('API_PORT', 5000))
    host = os.getenv('API_HOST', '0.0.0.0')
    debug = os.getenv('API_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug, host=host, port=port)