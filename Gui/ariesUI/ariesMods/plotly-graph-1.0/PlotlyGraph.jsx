import React, { useEffect, useRef } from 'react';

const PlotlyGraph = ({ streamId }) => {
  const graphDiv = useRef(null);

  useEffect(() => {
    // Initialize Plotly graph
    if (graphDiv.current && window.Plotly) {
      const initialData = [
        {
          x: [], // X-axis data (e.g., timestamps)
          y: [], // Y-axis data (e.g., sensor values)
          type: 'scatter',
          mode: 'lines+markers',
          name: 'Sensor Data',
        },
      ];

      const layout = {
        title: 'Real-Time Plotly Graph',
        xaxis: { title: 'Time' },
        yaxis: { title: 'Value' },
      };

      // Create initial Plotly plot
      window.Plotly.newPlot(graphDiv.current, initialData, layout);
    }
  }, []);

  useEffect(() => {
    if (!streamId) return;

    const [moduleId, streamName] = streamId.split('.');

    const updateInterval = setInterval(() => {
      if (
        window.GlobalData?.data?.[moduleId]?.streams?.[streamName] &&
        graphDiv.current &&
        window.Plotly
      ) {
        const value = window.GlobalData.data[moduleId].streams[streamName].value;
        const time = new Date().toLocaleTimeString(); // Example timestamp

        // Append new data to the graph
        window.Plotly.extendTraces(
          graphDiv.current,
          { x: [[time]], y: [[value]] },
          [0] // Trace index to update
        );
      }
    }, 100); // Update every 100ms

    // Cleanup interval on unmount
    return () => clearInterval(updateInterval);
  }, [streamId]);

  return <div ref={graphDiv} style={{ width: '100%', height: '400px' }} />;
};

export default PlotlyGraph;
