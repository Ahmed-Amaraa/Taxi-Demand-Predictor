import React, { useEffect, useState } from 'react';
import { compareAllModels } from '../services/api';
import '../styles/components.css';
import '../styles/pages.css';

const ComparePage = () => {
  const [comparison, setComparison] = useState(null);
  const [bestModel, setBestModel] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expandedModel, setExpandedModel] = useState(null);

  useEffect(() => {
    fetchComparison();
  }, []);

  const fetchComparison = async () => {
    setLoading(true);
    try {
      const response = await compareAllModels();
      const data = response.data.data || response.data;
      setComparison(data);
      
      // Extraire le meilleur modèle
      if (data.best_model && data.best_model.comparison) {
        setBestModel(data.best_model.comparison);
      }
      setError(null);
    } catch (err) {
      setError('Erreur lors du chargement de la comparaison');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const formatMetric = (value) => {
    if (value === null || value === undefined) return 'N/A';
    return typeof value === 'number' ? value.toFixed(4) : value;
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString('fr-FR');
  };

  if (loading) return <div className="loading">Chargement de la comparaison...</div>;

  if (!comparison || !comparison.comparison || comparison.comparison.length === 0) {
    return (
      <div className="compare-page">
        <div className="container">
          <h1>📈 Comparaison des modèles</h1>
          <div className="no-metrics">
            Aucun modèle à comparer. Veuillez d'abord entraîner des modèles.
          </div>
        </div>
      </div>
    );
  }

  const runs = comparison.comparison;

  // Grouper les résultats par modèle
  const modelGroups = {};
  runs.forEach(run => {
    if (!modelGroups[run.model_name]) {
      modelGroups[run.model_name] = [];
    }
    modelGroups[run.model_name].push(run);
  });

  return (
    <div className="compare-page">
      <div className="container">
        <h1>📊 Comparaison des modèles</h1>

        {error && <div className="alert alert-error">{error}</div>}

        {/* Meilleur modèle */}
        {bestModel && (
          <div className="comparison-header">
            <h2>🏆 Meilleur modèle global</h2>
            <div className="best-model-info">
              <h3>{Object.keys(bestModel)[0]}</h3>
              <p>
                Run ID: <code>{bestModel[Object.keys(bestModel)[0]].run_id?.slice(0, 12)}...</code>
              </p>
              <div className="best-model-metrics">
                <div className="best-model-metrics-item">
                  <strong>
                    {formatMetric(bestModel[Object.keys(bestModel)[0]].metrics?.r2)}
                  </strong>
                  <p>R² Score</p>
                </div>
                <div className="best-model-metrics-item">
                  <strong>
                    {formatMetric(bestModel[Object.keys(bestModel)[0]].metrics?.rmse)}
                  </strong>
                  <p>RMSE</p>
                </div>
                <div className="best-model-metrics-item">
                  <strong>
                    {formatMetric(bestModel[Object.keys(bestModel)[0]].metrics?.mae)}
                  </strong>
                  <p>MAE</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Tableau de comparaison */}
        <div className="comparison-table">
          <h2>📋 Détails de tous les modèles</h2>
          <table>
            <thead>
              <tr>
                <th>Modèle</th>
                <th>R² Score</th>
                <th>RMSE</th>
                <th>MAE</th>
                <th>Statut</th>
                <th>Date</th>
              </tr>
            </thead>
            <tbody>
              {runs.map((run, idx) => (
                <tr 
                  key={idx}
                  style={{ cursor: 'pointer' }}
                  onClick={() => setExpandedModel(expandedModel === idx ? null : idx)}
                >
                  <td>
                    <strong>{run.model_name}</strong>
                  </td>
                  <td>
                    <span className="metric-badge">
                      {formatMetric(run.metrics?.r2)}
                    </span>
                  </td>
                  <td>
                    <span className="metric-badge">
                      {formatMetric(run.metrics?.rmse)}
                    </span>
                  </td>
                  <td>
                    <span className="metric-badge">
                      {formatMetric(run.metrics?.mae)}
                    </span>
                  </td>
                  <td>{run.status || '✅ Complété'}</td>
                  <td>{formatDate(run.start_time)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Résumé par modèle */}
        <div className="comparison-header" style={{ marginTop: '2rem' }}>
          <h2>📊 Résumé par modèle</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem', marginTop: '1.5rem' }}>
            {Object.entries(modelGroups).map(([modelName, modelRuns]) => {
              const bestRun = modelRuns.reduce((best, run) => 
                (run.metrics?.r2 || 0) > (best.metrics?.r2 || 0) ? run : best
              );
              
              return (
                <div 
                  key={modelName}
                  style={{
                    background: '#f9f9f9',
                    padding: '1.5rem',
                    borderRadius: '8px',
                    border: '1px solid #eee'
                  }}
                >
                  <h3 style={{ color: '#667eea', marginBottom: '1rem' }}>
                    {modelName}
                  </h3>
                  <div style={{ fontSize: '0.9rem' }}>
                    <p><strong>Nombre d'entraînements:</strong> {modelRuns.length}</p>
                    <p>
                      <strong>Meilleur R²:</strong>{' '}
                      <span className="metric-badge">
                        {formatMetric(bestRun.metrics?.r2)}
                      </span>
                    </p>
                    <p>
                      <strong>Meilleur RMSE:</strong>{' '}
                      <span className="metric-badge">
                        {formatMetric(bestRun.metrics?.rmse)}
                      </span>
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Visualisations comparatives */}
        {comparison.visualizations && comparison.visualizations.length > 0 && (
          <div className="comparison-header" style={{ marginTop: '2rem' }}>
            <h2>📈 Graphiques comparatifs</h2>
            <div style={{ 
              marginTop: '2rem', 
              display: 'grid', 
              gridTemplateColumns: 'repeat(auto-fit, minmax(500px, 1fr))', 
              gap: '2rem' 
            }}>
              {comparison.visualizations.map((viz, idx) => (
                <div key={idx} style={{ background: '#f9f9f9', padding: '1rem', borderRadius: '8px' }}>
                  <h3 style={{ marginBottom: '1rem', color: '#333' }}>
                    {viz.description}
                  </h3>
                  {viz.type === 'png' ? (
                    <img
                      src={viz.file_path}
                      alt={viz.description}
                      style={{
                        maxWidth: '100%',
                        height: 'auto',
                        borderRadius: '4px',
                        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                      }}
                    />
                  ) : (
                    <iframe
                      src={viz.file_path}
                      title={viz.description}
                      style={{
                        width: '100%',
                        height: '500px',
                        border: 'none',
                        borderRadius: '4px',
                      }}
                    />
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        <div style={{ marginTop: '2rem', textAlign: 'center' }}>
          <button 
            className="train-btn" 
            onClick={fetchComparison}
            style={{ maxWidth: '200px' }}
          >
            🔄 Rafraîchir
          </button>
        </div>
      </div>
    </div>
  );
};

export default ComparePage;