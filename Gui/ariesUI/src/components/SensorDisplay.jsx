// src/components/SensorDisplay.jsx
import React from 'react';

const SensorDisplay = ({ streamId }) => {
  return (
    <div className="sensor-display">
      <h3>Stream Display</h3>
      <p>Monitoring Stream: {streamId}</p>
      {/* Add your sensor display logic here */}
    </div>
  );
};

export default SensorDisplay;
