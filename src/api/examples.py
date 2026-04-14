"""
Advanced API example with more features
This file shows how to extend the API with additional functionality
"""

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
import joblib
import numpy as np
from datetime import datetime
import json

# Example of extended request/response models

class ExtendedPredictionInput(BaseModel):
    """Extended prediction input with metadata"""
    features: List[float] = Field(..., description="Model features")
    timestamp: Optional[datetime] = None
    metadata: Optional[Dict[str, str]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "features": [0.5, 1.2, 0.3, 2.1, 0.8, 1.5, 0.9, 0.6, 1.1, 0.4],
                "timestamp": "2024-01-15T10:30:00",
                "metadata": {"location": "downtown", "weather": "rainy"}
            }
        }

class PredictionWithConfidence(BaseModel):
    """Prediction with confidence score"""
    prediction: float
    confidence: float
    model_version: str
    timestamp: datetime

# Example endpoints that could be added

async def predict_with_confidence(data: ExtendedPredictionInput):
    """
    Extended prediction with confidence estimation
    You can implement this by:
    1. Using ensemble models
    2. Using quantile regression
    3. Using bootstrapping
    """
    # This is a placeholder implementation
    prediction = 42.5
    confidence = 0.95
    return PredictionWithConfidence(
        prediction=prediction,
        confidence=confidence,
        model_version="1.0.0",
        timestamp=datetime.now()
    )

async def batch_predict_with_logging(data: List[Dict]):
    """
    Batch prediction with detailed logging
    """
    results = []
    for item in data:
        # Process each item
        result = {
            "input": item,
            "prediction": 42.5,
            "timestamp": datetime.now().isoformat()
        }
        results.append(result)
    return results

async def predict_with_feature_importance(data: List[float]):
    """
    Prediction with feature importance
    Shows which features contributed most to the prediction
    """
    # This would require access to model's feature importance
    # Works with tree-based models (RandomForest, XGBoost, etc.)
    
    prediction = 42.5
    feature_importance = [0.15, 0.08, 0.12, 0.18, 0.10, 0.09, 0.11, 0.07, 0.06, 0.04]
    
    return {
        "prediction": prediction,
        "feature_importance": feature_importance,
        "top_features": sorted(
            enumerate(feature_importance),
            key=lambda x: x[1],
            reverse=True
        )[:3]
    }

# Usage in your main app:
"""
app.post("/predict-advanced")(predict_with_confidence)
app.post("/batch-predict-logging")(batch_predict_with_logging)
app.get("/predict-with-importance")(predict_with_feature_importance)
"""
