import React from 'react'
import '../styles/ModelInfo.css'

function ModelInfo({ modelInfo }) {
  return (
    <div className="model-info">
      <h3>Model Information</h3>
      <div className="info-grid">
        <div className="info-item">
          <span className="label">Model Type:</span>
          <span className="value">{modelInfo.model_type}</span>
        </div>
        <div className="info-item">
          <span className="label">Status:</span>
          <span className={`status ${modelInfo.status}`}>
            {modelInfo.status}
          </span>
        </div>
      </div>
    </div>
  )
}

export default ModelInfo
