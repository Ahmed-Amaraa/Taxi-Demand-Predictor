import React from 'react'
import '../styles/PredictionResult.css'

function PredictionResult({ prediction }) {
  const formatNumber = (num) => {
    return typeof num === 'number' ? num.toFixed(2) : 'N/A'
  }

  return (
    <div className="prediction-result">
      <h2>Prediction Result</h2>
      <div className="result-card">
        <div className="result-value">
          <span className="label">Predicted Taxi Demand:</span>
          <span className="value">{formatNumber(prediction.prediction)}</span>
          <span className="unit">rides</span>
        </div>
        <div className="result-message">
          <p>{prediction.message}</p>
        </div>
      </div>
    </div>
  )
}

export default PredictionResult
