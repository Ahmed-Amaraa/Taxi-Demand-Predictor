import React, { useEffect, useState } from 'react';
import { getAvailableModels } from '../services/api';

const ModelSelector = ({ onModelSelect, selectedModel }) => {
  const [models, setModels] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchModels();
  }, []);

  const fetchModels = async () => {
    setLoading(true);
    try {
      const response = await getAvailableModels();
      setModels(response.data.data || response.data);
      setError(null);
    } catch (err) {
      setError('Erreur lors du chargement des modèles');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="loading">Chargement des modèles...</div>;
  if (error) return <div className="error">{error}</div>;

  const modelOrder = ['Linear', 'RF', 'XGB', 'ADA'];
  const sortedModels = Object.entries(models).sort((a, b) => {
    return modelOrder.indexOf(a[0]) - modelOrder.indexOf(b[0]);
  });

  return (
    <div className="model-selector">
      <h2>Sélectionnez un modèle</h2>
      <p className="model-selector-subtitle">Choisissez parmi les algorithmes d'apprentissage disponibles</p>
      <div className="model-grid">
        {sortedModels.map(([key, value]) => (
          <div
            key={key}
            className={`model-card ${selectedModel === key ? 'selected' : ''}`}
            onClick={() => onModelSelect(key)}
          >
            <div className="model-card-header">
              <h3>{key}</h3>
              {selectedModel === key && <span className="model-badge">✓ Sélectionné</span>}
            </div>
            <p className="model-description">
              {value.name || key}
            </p>
            {value.description && (
              <p className="description">{value.description}</p>
            )}
            <button 
              className="select-btn"
              onClick={(e) => {
                e.stopPropagation();
                onModelSelect(key);
              }}
            >
              {selectedModel === key ? 'Configurar' : 'Sélectionner'}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ModelSelector;