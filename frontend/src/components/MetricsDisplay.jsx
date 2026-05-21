import React, { useState } from 'react';

const MetricsDisplay = ({ metrics, modelName, featureImportances }) => {
  const [showFeatures, setShowFeatures] = useState(false);

  if (!metrics) {
    return <div className="no-metrics">Aucune métrique disponible</div>;
  }

  const formatMetric = (value) => {
    if (value === null || value === undefined) return 'N/A';
    return typeof value === 'number' ? value.toFixed(4) : value;
  };

  // Sort feature importances by importance
  const sortedFeatures = featureImportances 
    ? [...featureImportances.features]
        .map((feature, idx) => ({ 
          name: feature, 
          importance: featureImportances.importances[idx] 
        }))
        .sort((a, b) => b.importance - a.importance)
    : null;

  return (
    <div className="metrics-display">
      <h3>Métriques - {modelName}</h3>
      <div className="metrics-grid">
        <div className="metric-card">
          <h4>R² Score</h4>
          <p className="metric-value">
            {formatMetric(metrics.r2)}
          </p>
          <p className="metric-description">Coefficient de détermination</p>
        </div>

        <div className="metric-card">
          <h4>RMSE</h4>
          <p className="metric-value">
            {formatMetric(metrics.rmse)}
          </p>
          <p className="metric-description">Erreur quadratique moyenne</p>
        </div>

        <div className="metric-card">
          <h4>MAE</h4>
          <p className="metric-value">
            {formatMetric(metrics.mae)}
          </p>
          <p className="metric-description">Erreur absolue moyenne</p>
        </div>
      </div>

      {/* Feature Importances Section */}
      {sortedFeatures && sortedFeatures.length > 0 && (
        <div className="feature-importances-section">
          <button 
            className="features-toggle-btn"
            onClick={() => setShowFeatures(!showFeatures)}
          >
            <span className="toggle-icon">{showFeatures ? '▼' : '▶'}</span>
            Importance des Features ({sortedFeatures.length})
          </button>

          {showFeatures && (
            <div className="feature-importances-list">
              {sortedFeatures.map((feature, idx) => (
                <div key={idx} className="feature-importance-item">
                  <div className="feature-name">{feature.name}</div>
                  <div className="feature-bar-container">
                    <div 
                      className="feature-bar" 
                      style={{ 
                        width: `${(feature.importance / Math.max(...sortedFeatures.map(f => f.importance))) * 100}%` 
                      }}
                    />
                  </div>
                  <div className="feature-value">{feature.importance.toFixed(4)}</div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default MetricsDisplay;