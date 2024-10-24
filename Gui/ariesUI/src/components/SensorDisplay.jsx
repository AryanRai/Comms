// src/components/SensorDisplay.jsx
import React, { useState, useEffect } from 'react';

const SensorDisplay = ({ sensorId }) => {
  const [sensorValue, setSensorValue] = useState(null);

  useEffect(() => {
    // Example: Mocking sensor value coming from vanilla JS
    const interval = setInterval(() => {
      // Fetch or get sensor data dynamically
      const sensorData = window.getSensorData(sensorId); // Mock vanilla JS function
      setSensorValue(sensorData);
    }, 10); // Update every second

    return () => clearInterval(interval); // Cleanup on unmount
  }, [sensorId]);

  return (
    <div className="sensor-display">
      <h2>Sensor {sensorId}</h2>
      <p>Value: {sensorValue}</p>
    </div>
  );
};

export default SensorDisplay;
