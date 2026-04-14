"""
Utility functions for the API
"""
import numpy as np
from typing import List
import logging

logger = logging.getLogger(__name__)

def validate_features(features: List[float], expected_count: int = 10) -> bool:
    """
    Validate input features
    
    Args:
        features: List of features
        expected_count: Expected number of features
        
    Returns:
        True if valid, raises ValueError otherwise
    """
    if not isinstance(features, list):
        raise ValueError("Features must be a list")
    
    if len(features) != expected_count:
        raise ValueError(
            f"Expected {expected_count} features, got {len(features)}"
        )
    
    try:
        # Try to convert to float
        [float(f) for f in features]
    except (ValueError, TypeError):
        raise ValueError("All features must be numeric values")
    
    return True

def format_prediction(prediction: float, decimals: int = 2) -> float:
    """Format prediction to specified decimal places"""
    return round(float(prediction), decimals)

def log_prediction(features: List[float], prediction: float):
    """Log prediction for debugging"""
    logger.info(f"Prediction made - Features: {features}, Result: {prediction}")
