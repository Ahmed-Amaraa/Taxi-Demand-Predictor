import React, { useState } from 'react';

const VisualizationViewer = ({ visualizations }) => {
  const [selectedViz, setSelectedViz] = useState(0);

  if (!visualizations || visualizations.length === 0) {
    return <div className="no-viz">Aucune visualisation disponible</div>;
  }

  const current = visualizations[selectedViz];

  const getVizContent = () => {
    if (current.type === 'scatter' || current.type === 'residuals' || 
        current.type === 'histogram' || current.type === 'r2_comparison' || 
        current.type === 'box' || current.type === 'comparison' || current.type === 'bar') {
      // Les fichiers HTML/interactifs
      return (
        <iframe
          src={current.file_path}
          title={current.description}
          style={{ width: '100%', height: '600px', border: 'none' }}
        />
      );
    } else if (current.type === 'png') {
      // Les images PNG
      return (
        <img 
          src={current.file_path} 
          alt={current.description}
          style={{ maxWidth: '100%', height: 'auto' }}
        />
      );
    } else if (current.type === 'csv') {
      // Les fichiers CSV
      return (
        <div className="csv-viewer">
          <p>Fichier CSV : {current.description}</p>
          <a href={current.file_path} download className="download-btn">
            Télécharger CSV
          </a>
        </div>
      );
    }
  };

  return (
    <div className="visualization-viewer">
      <h3>Visualisations</h3>
      
      <div className="viz-tabs">
        {visualizations.map((viz, idx) => (
          <button
            key={idx}
            className={`tab ${selectedViz === idx ? 'active' : ''}`}
            onClick={() => setSelectedViz(idx)}
          >
            {viz.description}
          </button>
        ))}
      </div>

      <div className="viz-content">
        {getVizContent()}
      </div>
    </div>
  );
};

export default VisualizationViewer;