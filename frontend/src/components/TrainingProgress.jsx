import React, { useEffect, useState } from 'react';

const TrainingProgress = ({ isTraining, modelName }) => {
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    if (!isTraining) {
      setProgress(0);
      return;
    }

    const interval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 90) return prev;
        return prev + Math.random() * 30;
      });
    }, 500);

    return () => clearInterval(interval);
  }, [isTraining]);

  if (!isTraining) return null;

  return (
    <div style={{
      background: 'white',
      padding: '2rem',
      borderRadius: '8px',
      boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
    }}>
      <h3>Entraînement en cours...</h3>
      <p style={{ color: '#666', marginTop: '0.5rem' }}>
        Modèle: <strong>{modelName}</strong>
      </p>
      
      <div style={{
        background: '#f5f5f5',
        height: '10px',
        borderRadius: '5px',
        marginTop: '1rem',
        overflow: 'hidden',
      }}>
        <div style={{
          background: 'linear-gradient(90deg, #667eea 0%, #764ba2 100%)',
          height: '100%',
          width: `${Math.min(progress, 100)}%`,
          transition: 'width 0.3s ease',
        }} />
      </div>
      
      <p style={{ fontSize: '0.9rem', color: '#999', marginTop: '0.5rem' }}>
        {Math.round(Math.min(progress, 100))}%
      </p>

      <div style={{
        display: 'flex',
        gap: '0.5rem',
        marginTop: '1rem',
      }}>
        <div style={{
          width: '8px',
          height: '8px',
          borderRadius: '50%',
          background: '#667eea',
          animation: 'pulse 1.5s infinite',
        }} />
        <span style={{ color: '#666' }}>Veuillez patienter...</span>
      </div>

      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }
      `}</style>
    </div>
  );
};

export default TrainingProgress;