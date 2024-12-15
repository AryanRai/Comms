// GridContainer.jsx (or wherever your main grid logic is)
import React from 'react';
import { createRoot } from 'react-dom/client';
import SensorDisplay from './SensorDisplay';

const GridContainer = () => {
  // Your existing grid setup and state management

  const attachStreamView = (gridId, streamId) => {
    // Get the values from the input elements if they are passed
    const gridIdValue = gridId?.value || gridId;
    const streamIdValue = streamId?.value || streamId;

    console.log("Attaching stream view:", {gridId: gridIdValue, streamId: streamIdValue});

    // Find the grid element by gs-id attribute
    const gridElement = document.querySelector(`[gs-id="${gridIdValue}"]`);

    if (gridElement) {
      // Find the content div within the grid item
      const contentDiv = gridElement.querySelector('.grid-stack-item-content');
      if (!contentDiv) {
        console.error('Grid item content div not found');
        return;
      }

      // Create a new div to hold the SensorDisplay component
      const sensorContainer = document.createElement('div');
      sensorContainer.className = 'sensor-container';
      contentDiv.appendChild(sensorContainer);

      // Create root and render using the new API
      const root = createRoot(sensorContainer);
      root.render(<SensorDisplay streamId={streamIdValue} />);
    } else {
      console.error(`Grid with gs-id "${gridIdValue}" not found`);
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
