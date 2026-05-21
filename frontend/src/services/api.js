import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Modèles
export const getAvailableModels = () => api.get('/models/available');
export const listAllModels = () => api.get('/models');
export const getModelInfo = (modelName) => api.get(`/models/${modelName}`);

// Entraînement
export const trainModel = (modelName, hyperparams) =>
  api.post('/train', {
    model_name: modelName,
    hyperparams: hyperparams,
  });

// Résultats
export const getAllResults = () => api.get('/results');
export const getModelResults = (modelName) => api.get(`/results/${modelName}`);
export const compareAllModels = () => api.get('/results/compare/all');

// Rollback
export const rollbackModel = (modelName, version) =>
  api.post(`/models/rollback`, {
    model_name: modelName,
    version: version,
  });

// Predictions
export const getBestModels = () => api.get('/best-models');
export const makePrediction = (modelType, features) =>
  api.post('/predict', {
    model_type: modelType,
    features: features,
  });

export default api;