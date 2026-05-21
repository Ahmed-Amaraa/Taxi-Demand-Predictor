import React from 'react';

const ModelComparison = ({ models }) => {
  if (!models || models.length === 0) {
    return <div className="no-metrics">Aucun modèle à comparer</div>;
  }

  const formatMetric = (value) => {
    if (value === null || value === undefined) return 'N/A';
    return typeof value === 'number' ? value.toFixed(4) : value;
  };

  // Trouver le meilleur pour chaque métrique
  const bestR2 = Math.max(...models.map(m => m.metrics?.r2 || 0));
  const lowestRMSE = Math.min(...models.map(m => m.metrics?.rmse || Infinity));
  const lowestMAE = Math.min(...models.map(m => m.metrics?.mae || Infinity));

  return (
    <div style={{ background: 'white', padding: '2rem', borderRadius: '8px' }}>
      <h3>Comparaison des performances</h3>
      <table style={{ width: '100%', marginTop: '1rem' }}>
        <thead>
          <tr style={{ borderBottom: '2px solid #667eea' }}>
            <th style={{ padding: '1rem', textAlign: 'left' }}>Modèle</th>
            <th style={{ padding: '1rem', textAlign: 'center' }}>R² Score</th>
            <th style={{ padding: '1rem', textAlign: 'center' }}>RMSE</th>
            <th style={{ padding: '1rem', textAlign: 'center' }}>MAE</th>
          </tr>
        </thead>
        <tbody>
          {models.map((model, idx) => (
            <tr key={idx} style={{ borderBottom: '1px solid #eee' }}>
              <td style={{ padding: '1rem', fontWeight: 600 }}>
                {model.model_name}
              </td>
              <td style={{ padding: '1rem', textAlign: 'center' }}>
                <span 
                  style={{
                    padding: '0.25rem 0.75rem',
                    borderRadius: '20px',
                    background: model.metrics?.r2 === bestR2 ? '#d4edda' : '#e7f5ff',
                    color: model.metrics?.r2 === bestR2 ? '#155724' : '#667eea',
                    fontWeight: 500,
                  }}
                >
                  {formatMetric(model.metrics?.r2)}
                </span>
              </td>
              <td style={{ padding: '1rem', textAlign: 'center' }}>
                <span 
                  style={{
                    padding: '0.25rem 0.75rem',
                    borderRadius: '20px',
                    background: model.metrics?.rmse === lowestRMSE ? '#d4edda' : '#e7f5ff',
                    color: model.metrics?.rmse === lowestRMSE ? '#155724' : '#667eea',
                    fontWeight: 500,
                  }}
                >
                  {formatMetric(model.metrics?.rmse)}
                </span>
              </td>
              <td style={{ padding: '1rem', textAlign: 'center' }}>
                <span 
                  style={{
                    padding: '0.25rem 0.75rem',
                    borderRadius: '20px',
                    background: model.metrics?.mae === lowestMAE ? '#d4edda' : '#e7f5ff',
                    color: model.metrics?.mae === lowestMAE ? '#155724' : '#667eea',
                    fontWeight: 500,
                  }}
                >
                  {formatMetric(model.metrics?.mae)}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default ModelComparison;