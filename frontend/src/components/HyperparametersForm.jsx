import React, { useState, useEffect } from 'react';
import { getAvailableModels } from '../services/api';

const HyperparametersForm = ({ modelName, onSubmit, loading }) => {
  const [hyperparams, setHyperparams] = useState({});
  const [modelInfo, setModelInfo] = useState(null);
  const [limits, setLimits] = useState({});

  useEffect(() => {
    if (modelName) {
      fetchModelInfo();
    }
  }, [modelName]);

  const fetchModelInfo = async () => {
    try {
      const response = await getAvailableModels();
      const models = response.data.data || response.data;
      if (models[modelName]) {
        setModelInfo(models[modelName]);
        setHyperparams(models[modelName].hyperparams || {});
        setLimits(models[modelName].limits || {});
      }
    } catch (err) {
      console.error('Erreur lors du chargement des infos du modèle', err);
    }
  };

  const handleParamChange = (paramName, value) => {
    setHyperparams({
      ...hyperparams,
      [paramName]: isNaN(value) ? value : parseFloat(value),
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(hyperparams);
  };

  if (!modelInfo) {
    return <div>Chargement des paramètres...</div>;
  }

  return (
    <form className="hyperparams-form" onSubmit={handleSubmit}>
      <h2>Hyperparamètres pour {modelName}</h2>
      
      <div className="params-container">
        {Object.entries(hyperparams).map(([paramName, value]) => {
          const limit = limits[paramName];
          
          return (
            <div key={paramName} className="param-group">
              <label htmlFor={paramName}>
                {paramName}
                {limit && (
                  <span className="param-range">
                    ({limit[0]} - {limit[1]})
                  </span>
                )}
              </label>
              
              {typeof value === 'boolean' ? (
                <input
                  type="checkbox"
                  id={paramName}
                  checked={value}
                  onChange={(e) => handleParamChange(paramName, e.target.checked)}
                />
              ) : (
                <input
                  type={Number.isInteger(value) ? 'number' : 'number'}
                  id={paramName}
                  value={value}
                  step={Number.isInteger(value) ? '1' : '0.01'}
                  min={limit ? limit[0] : undefined}
                  max={limit ? limit[1] : undefined}
                  onChange={(e) => handleParamChange(paramName, e.target.value)}
                  required
                />
              )}
            </div>
          );
        })}
      </div>

      <button 
        type="submit" 
        className="train-btn"
        disabled={loading}
      >
        {loading ? 'Entraînement en cours...' : 'Entraîner le modèle'}
      </button>
    </form>
  );
};

export default HyperparametersForm;