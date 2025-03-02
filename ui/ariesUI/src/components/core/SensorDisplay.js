// src/components/SensorDisplay.js
import React, { useState, useEffect } from 'react';

const SensorDisplay = ({ streamId }) => {
  const [sensorValue, setSensorValue] = useState(null);
  
  useEffect(() => {
    // Subscribe to stream updates when component mounts
    if (!streamId) return;

    const [moduleId, streamName] = streamId.split('.');
    
    // Setup update interval
    const updateInterval = setInterval(() => {
      // Check if GlobalData exists and has the required data
      if (window.GlobalData?.data?.[moduleId]?.streams?.[streamName]) {
        setSensorValue(window.GlobalData.data[moduleId].streams[streamName].value);
      }
    }, 100); // Update every 100ms

    // Cleanup interval on unmount
    return () => clearInterval(updateInterval);
  }, [streamId]); // Re-run effect if streamId changes

  return (
    <div className="sensor-display">
      <h3>Stream Display</h3>
      <p>Monitoring Stream: {streamId}</p>
      <p>Current Value: {sensorValue !== null ? sensorValue : 'No data'}</p>
    </div>
  );
};

export default SensorDisplay;
