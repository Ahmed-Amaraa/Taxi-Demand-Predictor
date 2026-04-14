import React, { useState, useEffect } from 'react'
import PredictionForm from './components/PredictionForm'
import ModelInfo from './components/ModelInfo'
import PredictionResult from './components/PredictionResult'
import './App.css'

function App() {
  const [prediction, setPrediction] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [modelInfo, setModelInfo] = useState(null)
  const [apiHealthy, setApiHealthy] = useState(false)

  // Check API health on component mount
  useEffect(() => {
    checkApiHealth()
  }, [])

  const checkApiHealth = async () => {
    try {
      const response = await fetch('http://localhost:8000/health')
      if (response.ok) {
        setApiHealthy(true)
        // Fetch model info if API is healthy
        fetchModelInfo()
      }
    } catch (err) {
      setApiHealthy(false)
      console.error('API not available:', err)
    }
  }

  const fetchModelInfo = async () => {
    try {
      const response = await fetch('http://localhost:8000/model-info')
      if (response.ok) {
        const data = await response.json()
        setModelInfo(data)
      }
    } catch (err) {
      console.error('Failed to fetch model info:', err)
    }
  }

  const handlePrediction = async (features) => {
    setLoading(true)
    setError(null)
    setPrediction(null)

    try {
      const response = await fetch('http://localhost:8000/predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ features }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Prediction failed')
      }

      const data = await response.json()
      setPrediction(data)
    } catch (err) {
      setError(err.message)
      console.error('Prediction error:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>🚕 Taxi Demand Predictor</h1>
        <p>Predict taxi demand using machine learning</p>
      </header>

      <main className="app-main">
        {!apiHealthy && (
          <div className="alert alert-error">
            <strong>⚠️ API Connection Error</strong>
            <p>Please ensure the FastAPI server is running on http://localhost:8000</p>
            <button onClick={checkApiHealth}>Retry Connection</button>
          </div>
        )}

        {apiHealthy && (
          <>
            {modelInfo && <ModelInfo modelInfo={modelInfo} />}
            
            <div className="container">
              <PredictionForm 
                onPredict={handlePrediction} 
                loading={loading}
              />
              
              {error && (
                <div className="alert alert-error">
                  <strong>Error:</strong> {error}
                </div>
              )}
              
              {prediction && (
                <PredictionResult prediction={prediction} />
              )}
            </div>
          </>
        )}
      </main>

      <footer className="app-footer">
        <p>Taxi Demand Prediction System © 2024</p>
      </footer>
    </div>
  )
}

export default App
