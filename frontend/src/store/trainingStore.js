import create from 'zustand';

export const useTrainingStore = create((set) => ({
  // État de l'entraînement
  isTraining: false,
  currentModel: null,
  currentRun: null,
  
  // Résultats
  allResults: [],
  modelResults: {},
  comparison: null,
  
  // Visualisations
  visualizations: [],
  
  // Actions
  setIsTraining: (isTraining) => set({ isTraining }),
  setCurrentModel: (model) => set({ currentModel: model }),
  setCurrentRun: (run) => set({ currentRun: run }),
  
  setAllResults: (results) => set({ allResults: results }),
  setModelResults: (results) => set({ modelResults: results }),
  setComparison: (comparison) => set({ comparison }),
  
  setVisualizations: (visualizations) => set({ visualizations }),
  addVisualization: (viz) =>
    set((state) => ({
      visualizations: [...state.visualizations, viz],
    })),
  
  clearState: () =>
    set({
      isTraining: false,
      currentModel: null,
      currentRun: null,
      allResults: [],
      modelResults: {},
      comparison: null,
      visualizations: [],
    }),
}));