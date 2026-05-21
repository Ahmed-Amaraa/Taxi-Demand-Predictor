import React, { useEffect, useState } from 'react';
import { getAllResults, getModelResults } from '../services/api';
import '../styles/components.css';
import '../styles/pages.css';

const ResultsPage = () => {
  const [results, setResults] = useState([]);
  const [filteredResults, setFilteredResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filterModel, setFilterModel] = useState('all');
  const [sortBy, setSortBy] = useState('date');

  useEffect(() => {
    fetchResults();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [results, filterModel, sortBy]);

  const fetchResults = async () => {
    setLoading(true);
    try {
      const response = await getAllResults();
      const data = response.data.data || response.data;
      setResults(data.runs || []);
      setError(null);
    } catch (err) {
      setError('Erreur lors du chargement des résultats');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const applyFilters = () => {
    let filtered = results;

    // Filtrer par modèle
    if (filterModel !== 'all') {
      filtered = filtered.filter(r => r.model_name === filterModel);
    }

    // Trier
    if (sortBy === 'date') {
      filtered.sort((a, b) => new Date(b.start_time) - new Date(a.start_time));
    } else if (sortBy === 'r2') {
      filtered.sort((a, b) => (b.metrics?.r2 || 0) - (a.metrics?.r2 || 0));
    } else if (sortBy === 'rmse') {
      filtered.sort((a, b) => (a.metrics?.rmse || 0) - (b.metrics?.rmse || 0));
    }

    setFilteredResults(filtered);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString('fr-FR');
  };

  const formatMetric = (value) => {
    if (value === null || value === undefined) return 'N/A';
    return typeof value === 'number' ? value.toFixed(4) : value;
  };

  const uniqueModels = [...new Set(results.map(r => r.model_name))];

  if (loading) return <div className="loading">Chargement des résultats...</div>;

  return (
    <div className="results-page">
      <div className="container">
        <h1>📊 Résultats des entraînements</h1>

        {error && <div className="alert alert-error">{error}</div>}

        <div className="results-header">
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
            <div>
              <label style={{ fontWeight: 600, color: '#2c3e50' }}>Filtrer par modèle</label>
              <select 
                value={filterModel}
                onChange={(e) => setFilterModel(e.target.value)}
                style={{
                  width: '100%',
                  padding: '0.75rem 1rem',
                  border: '2px solid #e0e7ff',
                  borderRadius: '6px',
                  marginTop: '0.5rem',
                  fontFamily: 'inherit',
                  fontSize: '0.95rem',
                  backgroundColor: '#fafbff',
                  cursor: 'pointer',
                  transition: 'all 0.3s ease'
                }}
              >
                <option value="all">Tous les modèles</option>
                {uniqueModels.map(model => (
                  <option key={model} value={model}>{model}</option>
                ))}
              </select>
            </div>

            <div>
              <label style={{ fontWeight: 600, color: '#2c3e50' }}>Trier par</label>
              <select 
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                style={{
                  width: '100%',
                  padding: '0.75rem 1rem',
                  border: '2px solid #e0e7ff',
                  borderRadius: '6px',
                  marginTop: '0.5rem',
                  fontFamily: 'inherit',
                  fontSize: '0.95rem',
                  backgroundColor: '#fafbff',
                  cursor: 'pointer',
                  transition: 'all 0.3s ease'
                }}
              >
                <option value="date">Date (récent)</option>
                <option value="r2">R² Score (meilleur)</option>
                <option value="rmse">RMSE (meilleur)</option>
              </select>
            </div>
          </div>

          <h2>Total : {filteredResults.length} résultat(s)</h2>
          <button 
            className="train-btn" 
            onClick={fetchResults}
            style={{ marginTop: '1rem', maxWidth: '200px' }}
          >
            🔄 Rafraîchir
          </button>
        </div>

        {filteredResults.length === 0 ? (
          <div className="no-metrics">
            Aucun résultat d'entraînement disponible
          </div>
        ) : (
          <div className="results-grid">
            {filteredResults.map((result, idx) => (
              <div key={idx} className="result-card">
                <h3>🤖 {result.model_name}</h3>
                
                <div className="result-meta">
                  <strong>Run ID:</strong> 
                  <br />
                  <code style={{ fontSize: '0.85rem', color: '#667eea' }}>
                    {result.run_id?.slice(0, 12)}...
                  </code>
                </div>
                
                <div className="result-meta">
                  <strong>📅 Date:</strong> {formatDate(result.start_time)}
                </div>

                <div className="result-meta">
                  <strong>Durée:</strong> {Math.round(result.duration_ms / 1000)}s
                </div>

                <div className="result-meta">
                  <strong>Statut:</strong>{' '}
                  <span className="metric-badge" style={{ 
                    background: result.status === 'completed' ? '#d4edda' : '#fff3cd',
                    color: result.status === 'completed' ? '#155724' : '#856404'
                  }}>
                    {result.status || 'Complété'}
                  </span>
                </div>

                <div className="result-metrics">
                  <div className="result-metric-item">
                    <strong>{formatMetric(result.metrics?.r2)}</strong>
                    <small>R² Score</small>
                  </div>
                  <div className="result-metric-item">
                    <strong>{formatMetric(result.metrics?.rmse)}</strong>
                    <small>RMSE</small>
                  </div>
                  <div className="result-metric-item">
                    <strong>{formatMetric(result.metrics?.mae)}</strong>
                    <small>MAE</small>
                  </div>
                </div>

                {result.params && Object.keys(result.params).length > 0 && (
                  <details style={{ marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid #eee' }}>
                    <summary style={{ fontWeight: 600, cursor: 'pointer' }}>
                      ⚙️ Hyperparamètres
                    </summary>
                    <div style={{ fontSize: '0.85rem', color: '#666', marginTop: '0.5rem' }}>
                      {Object.entries(result.params).map(([key, value]) => (
                        <div key={key} style={{ marginBottom: '0.25rem' }}>
                          <strong>{key}:</strong> {String(value)}
                        </div>
                      ))}
                    </div>
                  </details>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ResultsPage;