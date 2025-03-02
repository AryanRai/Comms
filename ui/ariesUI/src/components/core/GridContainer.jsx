// GridContainer.jsx
import React from 'react';
import { createRoot } from 'react-dom/client';
import SensorDisplay from './SensorDisplay';

const GridContainer = () => {
  const AttachStreamView = (gridId, streamId, widgetType) => {
    const gridIdValue = gridId?.value || gridId;
    const streamIdValue = streamId?.value || streamId;
    const widgetTypeValue = widgetType?.value || widgetType || "GraphDisplay";

    console.log("Attaching stream view:", { gridId: gridIdValue, streamId: streamIdValue, widgetType: widgetTypeValue });

    const gridElement = document.querySelector(`[gs-id="${gridIdValue}"]`);
    if (!gridElement) {
      console.error(`Grid with gs-id "${gridIdValue}" not found`);
      return;
    }

    const contentDiv = gridElement.querySelector('.grid-stack-item-content');
    if (!contentDiv) {
      console.error('Grid item content div not found');
      return;
    }

    const componentContainer = document.createElement('div');
    componentContainer.className = 'component-container';
    contentDiv.appendChild(componentContainer);

    const root = createRoot(componentContainer);

    if (widgetTypeValue === "SensorDisplay") {
      root.render(<SensorDisplay streamId={streamIdValue} />);
    } else if (widgetTypeValue === "GraphDisplay") {
      if (window.GraphDisplay) {
        root.render(<window.GraphDisplay streamId={streamIdValue} />);
      } else {
        root.render(<div>Loading graph component...</div>);
        const checkInterval = setInterval(() => {
          if (window.GraphDisplay) {
            root.render(<window.GraphDisplay streamId={streamIdValue} />);
            clearInterval(checkInterval);
          }
        }, 100);
      }
    } else {
      root.render(<div>Unknown widget type: {widgetTypeValue}</div>);
    }

    if (window.subscribeToStream) {
      const [moduleId, streamName] = streamIdValue.split('.');
      window.subscribeToStream(moduleId, streamName);
    }
  };

  window.AttachStreamView = AttachStreamView;

  return (
    <div className="grid-stack">
      {/* Your existing grid items */}
    </div>
  );
};

export default GridContainer;