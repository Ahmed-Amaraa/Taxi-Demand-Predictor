from typing import Dict, Any, Tuple

class HyperparamValidator:
    """Validateur pour les hyperparamètres"""
    
    # Limites des hyperparamètres pour chaque modèle
    LIMITS = {
        "Linear": {
            # Pas de hyperparamètres
        },
        "RF": {
            "n_estimators": (10, 1000),
            "max_depth": (1, 50),
            "min_samples_split": (2, 20),
            "min_samples_leaf": (1, 10),
            "random_state": (0, 100)
        },
        "XGB": {
            "n_estimators": (10, 1000),
            "max_depth": (1, 15),
            "learning_rate": (0.001, 1.0),
            "subsample": (0.1, 1.0),
            "colsample_bytree": (0.1, 1.0),
            "random_state": (0, 100)
        },
        "ADA": {
            "n_estimators": (10, 1000),
            "learning_rate": (0.001, 2.0),
            "random_state": (0, 100)
        }
    }
    
    @staticmethod
    def validate_model_name(model_name: str) -> Tuple[bool, str]:
        """Valide le nom du modèle"""
        valid_models = ["Linear", "RF", "XGB", "ADA"]
        if model_name not in valid_models:
            return False, f"Model must be one of {valid_models}"
        return True, "OK"
    
    @staticmethod
    def validate_hyperparams(model_name: str, hyperparams: Dict) -> Tuple[bool, str]:
        """Valide les hyperparamètres pour un modèle"""
        
        # Vérifier le modèle
        is_valid, msg = HyperparamValidator.validate_model_name(model_name)
        if not is_valid:
            return False, msg
        
        # Linear n'a pas de hyperparamètres
        if model_name == "Linear" and hyperparams:
            return False, "Linear Regression has no hyperparameters"
        
        # Vérifier les limites
        if model_name in HyperparamValidator.LIMITS:
            limits = HyperparamValidator.LIMITS[model_name]
            
            for param, value in hyperparams.items():
                if param not in limits:
                    return False, f"Unknown parameter '{param}' for {model_name}"
                
                min_val, max_val = limits[param]
                if not (min_val <= value <= max_val):
                    return False, f"Parameter '{param}' must be between {min_val} and {max_val}, got {value}"
        
        return True, "OK"
    
    @staticmethod
    def get_default_hyperparams(model_name: str) -> Dict[str, Any]:
        """Retourne les hyperparamètres par défaut"""
        defaults = {
            "Linear": {},
            "RF": {
                "n_estimators": 100,
                "max_depth": 10,
                "min_samples_split": 2,
                "random_state": 42
            },
            "XGB": {
                "n_estimators": 100,
                "max_depth": 6,
                "learning_rate": 0.1,
                "subsample": 0.8,
                "random_state": 42
            },
            "ADA": {
                "n_estimators": 100,
                "learning_rate": 0.1,
                "random_state": 42
            }
        }
        return defaults.get(model_name, {})