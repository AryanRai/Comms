// react/App.js
import React from 'react';
import ReactDOM from 'react-dom';
import SensorDisplay from './components/SensorDisplay';
import GridContainer from './components/GridContainer';

const App = () => {
  // Attach the function to the window object for global access
  const attachStreamView = (gridId, streamId) => {
    const gridElement = document.getElementById(gridId);

    if (gridElement) {
      const sensorContainer = document.createElement('div');
      sensorContainer.className = 'grid-item';
      gridElement.appendChild(sensorContainer);

      ReactDOM.render(<SensorDisplay streamId={streamId} />, sensorContainer);
    } else {
      console.error(`Grid with ID ${gridId} not found`);
    }
  };

  // Set the attachStreamView function to the window object
  window.AttachStreamView = attachStreamView;

  return (
    
    <div>    
    <div>
    <h1>Sensor Dashboard</h1>
    <div id="sensor-readings">
      <SensorDisplay sensorId="1" />
    </div>
  </div>
      <GridContainer />
      {/* Other components can be added here */}
    </div>
  );
};

export default App;
