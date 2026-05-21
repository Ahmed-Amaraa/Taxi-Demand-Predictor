import React, { useState } from 'react';
import { trainModel } from '../services/api';
import { useTrainingStore } from '../store/trainingStore';
import ModelSelector from '../components/ModelSelector';
import HyperparametersForm from '../components/HyperparametersForm';
import MetricsDisplay from '../components/MetricsDisplay';
import VisualizationViewer from '../components/VisualizationViewer';
import '../styles/components.css';
import '../styles/pages.css';

const TrainPage = () => {
  const [selectedModel, setSelectedModel] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  
  const { setCurrentModel, setCurrentRun, setVisualizations } = useTrainingStore();
  const [trainResult, setTrainResult] = useState(null);

  const handleTrainSubmit = async (hyperparams) => {
    setLoading(true);
    setError(null);
    setSuccess(false);

    try {
      const response = await trainModel(selectedModel, hyperparams);
      const data = response.data.data || response.data;
      
      setTrainResult(data);
      setCurrentModel(selectedModel);
      setCurrentRun(data.run_id);
      setVisualizations(data.visualizations || []);
      setSuccess(true);
      
      // Smooth scroll to results
      setTimeout(() => {
        document.querySelector('.train-results')?.scrollIntoView({ behavior: 'smooth' });
      }, 100);
    } catch (err) {
      setError(
        err.response?.data?.error || 'Erreur lors de l\'entraînement du modèle'
      );
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="train-page">
      <div className="container">
        <h1>Entraîner un modèle</h1>

        {error && <div className="alert alert-error">{error}</div>}
        {success && (
          <div className="alert alert-success">
            Modèle entraîné avec succès !
          </div>
        )}

        {/* New Dynamic Model Selection Layout */}
        <div className="train-dynamic-layout">
          {/* Model Carousel Section */}
          <div className="model-carousel-section">
            <ModelSelector 
              selectedModel={selectedModel}
              onModelSelect={setSelectedModel}
            />
          </div>

          {/* Form and Results Section */}
          {selectedModel && (
            <div className="train-form-results-section">
              {/* Form on Left */}
              <div className="train-form-container">
                <HyperparametersForm
                  modelName={selectedModel}
                  onSubmit={handleTrainSubmit}
                  loading={loading}
                />
              </div>

              {/* Results on Right */}
              <div className="train-results-container">
                {trainResult ? (
                  <>
                    <MetricsDisplay 
                      metrics={trainResult.metrics}
                      modelName={selectedModel}
                      featureImportances={trainResult.feature_importances}
                    />
                  </>
                ) : (
                  <div className="placeholder-box">
                    <div className="placeholder-icon">📊</div>
                    <p>Les métriques d'entraînement s'afficheront ici</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Empty state when no model selected */}
          {!selectedModel && (
            <div className="empty-state">
              <div className="empty-state-icon">🤖</div>
              <h2>Sélectionnez un modèle pour commencer</h2>
              <p>Choisissez parmi les modèles disponibles ci-dessus et configurez les hyperparamètres</p>
            </div>
          )}
        </div>

        {/* Charts Section */}
        {trainResult && (
          <div className="train-results" style={{ marginTop: '3rem' }}>
            <h2>Visualisations</h2>
            {trainResult.visualizations && (
              <VisualizationViewer 
                visualizations={trainResult.visualizations}
              />
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default TrainPage;