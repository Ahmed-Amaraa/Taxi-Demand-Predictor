import React, { useState, useEffect } from 'react';
import { getBestModels, makePrediction } from '../services/api';
import '../styles/pages.css';
import '../styles/prediction.css';

const PredictionPage = () => {
  const [bestModels, setBestModels] = useState(null);
  const [selectedModel, setSelectedModel] = useState('Linear');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [loadingModels, setLoadingModels] = useState(true);

  // Form inputs
  const [features, setFeatures] = useState({
    hour: 10,
    day: 3,
    month: 4,
    zone: 5,
    lag_1: 15,
    lag_24: 20,
    global_lag_24: 500,
  });

  // Normalization constants (must match backend)
  const LAG_24_MIN = 1;
  const LAG_24_MAX = 131;
  const GLOBAL_LAG_24_MIN = 1;
  const GLOBAL_LAG_24_MAX = 915;

  // Calculate derived features
  const calculateDerivedFeatures = () => {
    const lag_24_norm = (features.lag_24 - LAG_24_MIN) / (LAG_24_MAX - LAG_24_MIN);
    const global_lag_24_norm = (features.global_lag_24 - GLOBAL_LAG_24_MIN) / (GLOBAL_LAG_24_MAX - GLOBAL_LAG_24_MIN);
    const diff = features.lag_24 - features.global_lag_24;

    return {
      lag_24_norm,
      global_lag_24_norm,
      diff,
    };
  };

  const derived = calculateDerivedFeatures();

  // Load best models on component mount
  useEffect(() => {
    fetchBestModels();
  }, []);

  const fetchBestModels = async () => {
    try {
      setLoadingModels(true);
      const response = await getBestModels();
      setBestModels(response.data.data);
      setError(null);
    } catch (err) {
      setError('Erreur lors du chargement des meilleurs modèles');
      console.error(err);
    } finally {
      setLoadingModels(false);
    }
  };

  const handleFeatureChange = (e) => {
    const { name, value } = e.target;
    setFeatures({
      ...features,
      [name]: parseFloat(value) || 0,
    });
  };

  const handlePredict = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setPrediction(null);

    try {
      const response = await makePrediction(selectedModel, features);
      setPrediction(response.data.data);
    } catch (err) {
      setError(
        err.response?.data?.error || 'Erreur lors de la prédiction'
      );
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const getModelDisplayName = (modelType) => {
    const names = {
      Linear: 'Linear Regression',
      RF: 'Random Forest',
      XGB: 'XGBoost',
    };
    return names[modelType] || modelType;
  };

  if (loadingModels) {
    return (
      <div className="prediction-page">
        <div className="container">
          <div className="loading-spinner">Chargement des modèles...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="prediction-page">
      <div className="container">
        <div className="prediction-header">
          <h1>🔮 Prédiction de Demande Taxi</h1>
          <p>
            Entrez les paramètres et choisissez un modèle pour prédire la
            demande de taxis
          </p>
        </div>

        <div className="prediction-content">
          {/* Left Side - Form */}
          <div className="prediction-form-section">
            <div className="card">
              <h2>Paramètres d'entrée</h2>

              {error && <div className="alert alert-error">{error}</div>}

              <form onSubmit={handlePredict}>
                {/* Model Selection */}
                <div className="form-group">
                  <label htmlFor="model-select">Modèle</label>
                  <select
                    id="model-select"
                    value={selectedModel}
                    onChange={(e) => setSelectedModel(e.target.value)}
                    className="form-select"
                  >
                    {bestModels &&
                      Object.keys(bestModels).map((modelType) => (
                        <option key={modelType} value={modelType}>
                          {getModelDisplayName(modelType)} (R² :{' '}
                          {bestModels[modelType].metrics.r2?.toFixed(3)})
                        </option>
                      ))}
                  </select>
                </div>

                {/* Features Grid */}
                <div className="features-grid">
                  {/* Hour */}
                  <div className="form-group">
                    <label htmlFor="hour">
                      Heure du jour <span className="unit">(0-23)</span>
                    </label>
                    <input
                      id="hour"
                      type="number"
                      name="hour"
                      min="0"
                      max="23"
                      value={features.hour}
                      onChange={handleFeatureChange}
                      className="form-input"
                    />
                  </div>

                  {/* Day */}
                  <div className="form-group">
                    <label htmlFor="day">
                      Jour de la semaine <span className="unit">(0-6)</span>
                    </label>
                    <input
                      id="day"
                      type="number"
                      name="day"
                      min="0"
                      max="6"
                      value={features.day}
                      onChange={handleFeatureChange}
                      className="form-input"
                    />
                    <small className="help-text">
                      0=Lundi, 6=Dimanche
                    </small>
                  </div>

                  {/* Month */}
                  <div className="form-group">
                    <label htmlFor="month">
                      Mois <span className="unit">(1-12)</span>
                    </label>
                    <input
                      id="month"
                      type="number"
                      name="month"
                      min="1"
                      max="12"
                      value={features.month}
                      onChange={handleFeatureChange}
                      className="form-input"
                    />
                  </div>

                  {/* Zone */}
                  <div className="form-group">
                    <label htmlFor="zone">
                      Zone <span className="unit">(0-29)</span>
                    </label>
                    <input
                      id="zone"
                      type="number"
                      name="zone"
                      min="0"
                      max="29"
                      value={features.zone}
                      onChange={handleFeatureChange}
                      className="form-input"
                    />
                  </div>

                  {/* Lag 1 */}
                  <div className="form-group">
                    <label htmlFor="lag_1">
                      Demande (h-1) <span className="unit">(courses)</span>
                    </label>
                    <input
                      id="lag_1"
                      type="number"
                      name="lag_1"
                      min="0"
                      value={features.lag_1}
                      onChange={handleFeatureChange}
                      className="form-input"
                    />
                  </div>

                  {/* Lag 24 - Local */}
                  <div className="form-group">
                    <label htmlFor="lag_24">
                      Demande zone (h-24) <span className="unit">(courses)</span>
                    </label>
                    <input
                      id="lag_24"
                      type="number"
                      name="lag_24"
                      min="1"
                      max="131"
                      value={features.lag_24}
                      onChange={handleFeatureChange}
                      className="form-input"
                    />
                  </div>

                  {/* Global Lag 24 */}
                  <div className="form-group">
                    <label htmlFor="global_lag_24">
                      Demande globale (h-24) <span className="unit">(courses)</span>
                    </label>
                    <input
                      id="global_lag_24"
                      type="number"
                      name="global_lag_24"
                      min="1"
                      max="915"
                      value={features.global_lag_24}
                      onChange={handleFeatureChange}
                      className="form-input"
                    />
                  </div>
                </div>

                {/* Calculated Features Display */}
                <div className="calculated-features">
                  <h3>Paramètres calculés</h3>
                  <div className="calculated-grid">
                    <div className="calculated-item">
                      <span className="calc-label">lag_24_norm:</span>
                      <span className="calc-value">{derived.lag_24_norm.toFixed(4)}</span>
                    </div>
                    <div className="calculated-item">
                      <span className="calc-label">global_lag_24_norm:</span>
                      <span className="calc-value">{derived.global_lag_24_norm.toFixed(4)}</span>
                    </div>
                    <div className="calculated-item">
                      <span className="calc-label">diff (lag_24 - global_lag_24):</span>
                      <span className="calc-value">{derived.diff.toFixed(0)}</span>
                    </div>
                  </div>
                </div>

                {/* Submit Button */}
                <button
                  type="submit"
                  className="btn btn-primary btn-large"
                  disabled={loading}
                >
                  {loading ? 'Prédiction en cours...' : '🚀 Prédire'}
                </button>
              </form>
            </div>
          </div>

          {/* Right Side - Results */}
          <div className="prediction-results-section">
            {prediction ? (
              <div className="card prediction-result">
                <div className="result-header">
                  <h2>Résultat de la prédiction</h2>
                  <span className="result-model">
                    {getModelDisplayName(prediction.model_type)}
                  </span>
                </div>

                {/* Main Prediction */}
                <div className="prediction-box">
                  <div className="prediction-label">Demande prédite</div>
                  <div className="prediction-value">
                    {Math.round(prediction.prediction)}
                    <span className="prediction-unit"> courses</span>
                  </div>
                </div>

                {/* Model Metrics */}
                <div className="metrics-section">
                  <h3>Performance du modèle</h3>
                  <div className="metrics-grid">
                    <div className="metric-card">
                      <div className="metric-label">R² Score</div>
                      <div className="metric-value">
                        {prediction.metrics.r2?.toFixed(4)}
                      </div>
                      <div className="metric-bar">
                        <div
                          className="metric-fill"
                          style={{
                            width: `${Math.min(prediction.metrics.r2 * 100, 100)}%`,
                          }}
                        ></div>
                      </div>
                    </div>

                    <div className="metric-card">
                      <div className="metric-label">RMSE</div>
                      <div className="metric-value">
                        {prediction.metrics.rmse?.toFixed(2)}
                      </div>
                    </div>

                    <div className="metric-card">
                      <div className="metric-label">MAE</div>
                      <div className="metric-value">
                        {prediction.metrics.mae?.toFixed(2)}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Input Summary */}
                <div className="input-summary">
                  <h3>Paramètres utilisés</h3>
                  <div className="summary-grid">
                    {Object.entries(prediction.input_features).map(
                      ([key, value]) => (
                        <div key={key} className="summary-item">
                          <span className="summary-label">{key}:</span>
                          <span className="summary-value">
                            {typeof value === 'number'
                              ? value.toFixed(2)
                              : value}
                          </span>
                        </div>
                      )
                    )}
                  </div>
                </div>

                {/* Confidence Indicator */}
                <div className="confidence-section">
                  <div className="confidence-label">Confiance du modèle</div>
                  <div className="confidence-bar">
                    <div
                      className="confidence-fill"
                      style={{
                        width: `${Math.min(prediction.metrics.r2 * 100, 100)}%`,
                        background: `hsl(${
                          Math.min(prediction.metrics.r2 * 120, 120)
                        }, 100%, 50%)`,
                      }}
                    ></div>
                  </div>
                  <div className="confidence-text">
                    {prediction.metrics.r2 > 0.8
                      ? '✅ Très élevée'
                      : prediction.metrics.r2 > 0.6
                      ? '⚠️ Élevée'
                      : prediction.metrics.r2 > 0.4
                      ? '⚠️ Modérée'
                      : '❌ Faible'}
                  </div>
                </div>
              </div>
            ) : (
              <div className="card empty-state">
                <div className="empty-icon">📊</div>
                <h3>Aucune prédiction</h3>
                <p>
                  Remplissez le formulaire et cliquez sur "Prédire" pour voir
                  les résultats
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Model Info Cards */}
        {bestModels && (
          <div className="model-comparison-section">
            <h2>Comparaison des meilleurs modèles</h2>
            <div className="model-cards-grid">
              {Object.entries(bestModels).map(([modelType, modelInfo]) => (
                <div
                  key={modelType}
                  className={`model-info-card ${
                    selectedModel === modelType ? 'active' : ''
                  }`}
                  onClick={() => setSelectedModel(modelType)}
                >
                  <h3>{getModelDisplayName(modelType)}</h3>
                  <div className="model-metrics">
                    <div className="metric">
                      <span className="metric-name">R²:</span>
                      <span className="metric-val">
                        {modelInfo.metrics.r2?.toFixed(4)}
                      </span>
                    </div>
                    <div className="metric">
                      <span className="metric-name">RMSE:</span>
                      <span className="metric-val">
                        {modelInfo.metrics.rmse?.toFixed(2)}
                      </span>
                    </div>
                    <div className="metric">
                      <span className="metric-name">MAE:</span>
                      <span className="metric-val">
                        {modelInfo.metrics.mae?.toFixed(2)}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PredictionPage;
