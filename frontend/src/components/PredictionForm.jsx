import React, { useState } from 'react'
import '../styles/PredictionForm.css'

function PredictionForm({ onPredict, loading }) {
  const [features, setFeatures] = useState(Array(10).fill(0))
  const [featureNames] = useState([
    'Zone',
    'Hour',
    'Day',
    'Month',
    'Lag_1',
    'Lag_24',
    'Global_lag_24',
    'Lag_24_norm',
    'Global_lag_24_norm',
    'Diff'
  ])

  const handleFeatureChange = (index, value) => {
    const newFeatures = [...features]
    newFeatures[index] = parseFloat(value) || 0
    setFeatures(newFeatures)
  }

  const handleRandomValues = () => {
    const randomFeatures = features.map(() => 
      parseFloat((Math.random() * 2).toFixed(2))
    )
    setFeatures(randomFeatures)
  }

  const handleReset = () => {
    setFeatures(Array(10).fill(0))
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    onPredict(features)
  }

  return (
    <div className="prediction-form">
      <h2>Input Features for Prediction</h2>
      <form onSubmit={handleSubmit}>
        <div className="features-grid">
          {features.map((value, index) => (
            <div key={index} className="feature-input-group">
              <label htmlFor={`feature-${index}`}>
                {featureNames[index]}
              </label>
              <input
                id={`feature-${index}`}
                type="number"
                step="0.1"
                value={value}
                onChange={(e) => handleFeatureChange(index, e.target.value)}
                disabled={loading}
              />
            </div>
          ))}
        </div>

        <div className="button-group">
          <button 
            type="submit" 
            disabled={loading}
            className="btn btn-primary"
          >
            {loading ? 'Predicting...' : 'Predict'}
          </button>
          <button 
            type="button" 
            onClick={handleRandomValues}
            disabled={loading}
            className="btn btn-secondary"
          >
            Random Values
          </button>
          <button 
            type="button" 
            onClick={handleReset}
            disabled={loading}
            className="btn btn-secondary"
          >
            Reset
          </button>
        </div>
      </form>
    </div>
  )
}

export default PredictionForm
