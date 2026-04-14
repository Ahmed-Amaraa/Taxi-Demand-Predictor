"""
FastAPI application to serve the taxi demand prediction model
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import joblib
import numpy as np
import os
from pathlib import Path

# Load the pre-trained model
MODEL_PATH = Path(__file__).parent.parent.parent / "models" / "taxi_demand.joblib"
model = joblib.load(MODEL_PATH)

# Initialize FastAPI app
app = FastAPI(
    title="Taxi Demand Prediction API",
    description="API to predict taxi demand",
    version="1.0.0"
)

# Add CORS middleware to allow requests from React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define request/response models
class PredictionInput(BaseModel):
    """Input features for prediction"""
    features: List[float]
    
    class Config:
        json_schema_extra = {
            "example": {
                "features": [0.5, 1.2, 0.3, 2.1, 0.8, 1.5, 0.9, 0.6, 1.1, 0.4]
            }
        }

class PredictionOutput(BaseModel):
    """Prediction output"""
    prediction: float
    message: str

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    model_loaded: bool

# API Endpoints
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    Returns status of the API and model
    """
    return {
        "status": "healthy",
        "model_loaded": model is not None
    }

@app.post("/predict", response_model=PredictionOutput)
async def predict(data: PredictionInput):
    """
    Predict taxi demand
    
    Args:
        data: PredictionInput with features list
        
    Returns:
        PredictionOutput with prediction value
        
    Raises:
        HTTPException: If prediction fails
    """
    try:
        # Convert input features to numpy array
        features_array = np.array(data.features).reshape(1, -1)
        
        # Make prediction
        prediction = model.predict(features_array)[0]
        
        return {
            "prediction": float(prediction),
            "message": f"Predicted taxi demand: {prediction:.2f}"
        }
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid input features: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction error: {str(e)}"
        )

@app.post("/batch-predict")
async def batch_predict(data: List[PredictionInput]):
    """
    Predict taxi demand for multiple inputs
    
    Args:
        data: List of PredictionInput objects
        
    Returns:
        List of predictions
    """
    try:
        if not data:
            raise ValueError("Empty batch")
        
        # Convert all features to numpy array
        features_list = [d.features for d in data]
        features_array = np.array(features_list)
        
        # Make predictions
        predictions = model.predict(features_array)
        
        return {
            "predictions": [float(p) for p in predictions],
            "count": len(predictions),
            "message": f"Predicted demand for {len(predictions)} inputs"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Batch prediction error: {str(e)}"
        )

@app.get("/model-info")
async def model_info():
    """
    Get information about the loaded model
    """
    return {
        "model_type": type(model).__name__,
        "model_path": str(MODEL_PATH),
        "status": "ready" if model else "not loaded"
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Taxi Demand Prediction API",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
