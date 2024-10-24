// GridContainer.jsx (or wherever your main grid logic is)
import React from 'react';
import ReactDOM from 'react-dom';
import SensorDisplay from './SensorDisplay';

const GridContainer = () => {
  // Your existing grid setup and state management

  const attachStreamView = (gridId, streamId) => {
    // Find the grid element by ID
    const gridElement = document.getElementById(gridId);

    if (gridElement) {
      // Create a new div to hold the SensorDisplay component
      const sensorContainer = document.createElement('div');
      sensorContainer.className = 'grid-item'; // Optional: Add any relevant classes or styles
      gridElement.appendChild(sensorContainer);

      // Render the SensorDisplay component into the new div
      ReactDOM.render(<SensorDisplay streamId={streamId} />, sensorContainer);
    } else {
      console.error(`Grid with ID ${gridId} not found`);
    }
  };

  // Attach the function to the window object for global access
  window.AttachStreamView = attachStreamView;

  return (
    <div className="grid-stack">
      {/* Your existing grid items and rendering logic */}
    </div>
  );
};

export default GridContainer;
