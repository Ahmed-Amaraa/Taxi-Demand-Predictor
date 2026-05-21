import json
import os
from datetime import datetime
import base64

class FileHelper:
    """Aide pour la gestion des fichiers"""
    
    @staticmethod
    def file_to_base64(file_path: str) -> str:
        """Convertit un fichier en base64 pour transmission"""
        try:
            with open(file_path, 'rb') as f:
                return base64.b64encode(f.read()).decode('utf-8')
        except Exception as e:
            raise Exception(f"Error converting file to base64: {e}")
    
    @staticmethod
    def ensure_directory(directory: str) -> bool:
        """Crée un répertoire s'il n'existe pas"""
        try:
            os.makedirs(directory, exist_ok=True)
            return True
        except Exception as e:
            raise Exception(f"Error creating directory: {e}")
    
    @staticmethod
    def get_file_size(file_path: str) -> str:
        """Récupère la taille d'un fichier en format lisible"""
        try:
            size_bytes = os.path.getsize(file_path)
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size_bytes < 1024.0:
                    return f"{size_bytes:.2f} {unit}"
                size_bytes /= 1024.0
            return f"{size_bytes:.2f} TB"
        except Exception as e:
            raise Exception(f"Error getting file size: {e}")

class DateTimeHelper:
    """Aide pour la gestion des dates"""
    
    @staticmethod
    def get_iso_timestamp() -> str:
        """Retourne le timestamp ISO courant"""
        return datetime.now().isoformat()
    
    @staticmethod
    def format_timestamp(timestamp_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
        """Formate un timestamp"""
        try:
            dt = datetime.fromisoformat(timestamp_str)
            return dt.strftime(format_str)
        except Exception as e:
            return timestamp_str

class MetricsHelper:
    """Aide pour les calculs de métriques"""
    
    @staticmethod
    def calculate_percentage_improvement(old_value: float, new_value: float) -> float:
        """Calcule le pourcentage d'amélioration"""
        if old_value == 0:
            return 0
        return ((new_value - old_value) / abs(old_value)) * 100
    
    @staticmethod
    def rank_models(models_list: list, metric: str = "r2", ascending: bool = False) -> list:
        """Classe les modèles par une métrique"""
        return sorted(
            models_list,
            key=lambda x: x['metrics'].get(metric, 0),
            ascending=ascending
        )

class ResponseHelper:
    """Aide pour formater les réponses"""
    
    @staticmethod
    def success_response(data: dict, message: str = "Success") -> dict:
        """Formate une réponse de succès"""
        return {
            "status": "success",
            "message": message,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def error_response(error: str, code: str = "ERROR") -> dict:
        """Formate une réponse d'erreur"""
        return {
            "status": "error",
            "error": error,
            "code": code,
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def paginate_results(items: list, page: int = 1, per_page: int = 10) -> dict:
        """Pagine les résultats"""
        total = len(items)
        start = (page - 1) * per_page
        end = start + per_page
        
        return {
            "items": items[start:end],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": (total + per_page - 1) // per_page
            }
        }