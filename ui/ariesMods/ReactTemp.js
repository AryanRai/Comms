// ui/ariesMods/GraphDisplay.js
import React, { useState, useEffect } from 'react';

console.log('importing GraphDisplay');
const GraphDisplay = ({ streamId }) => {
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
    <div className="graph-display">
      <h3>Graph Display</h3>
      <p>Monitoring Stream: {streamId}</p>
      <p>Current Value: {sensorValue !== null ? sensorValue : 'No data'}</p>
    </div>
  );
};

export default GraphDisplay;

// Modify the eval'd code to include this at the end
window.GraphDisplay = GraphDisplay;