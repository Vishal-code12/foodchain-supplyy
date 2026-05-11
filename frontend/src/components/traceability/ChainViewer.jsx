import React from 'react';
import './chainViewer.css';

const ChainViewer = ({ journey }) => {
  if (!journey || journey.length === 0) {
    return <div className="no-journey">No journey data available</div>;
  }

  return (
    <div className="chain-viewer">
      <h3>Product Journey</h3>
      <div className="timeline">
        {journey.map((step, index) => (
          <div key={step.step} className={`timeline-item ${step.action}`}>
            <div className="timeline-marker"></div>
            <div className="timeline-content">
              <h4>{step.description}</h4>
              <p className="timeline-meta">
                By: {step.user_name || step.from_user_name} 
                ({step.user_role || step.from_user_role})
              </p>
              <p className="timeline-date">
                {new Date(step.timestamp).toLocaleString()}
              </p>
              {step.quantity && (
                <p className="timeline-quantity">
                  Quantity: {step.quantity}
                </p>
              )}
              {step.block_hash && (
                <p className="timeline-block">
                  Block: <code>{step.block_hash.slice(0, 16)}...</code>
                </p>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ChainViewer;