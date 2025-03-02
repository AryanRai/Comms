// ui/ariesMods/GraphDisplay.js
console.log('importing GraphDisplay');
const GraphDisplay = ({ streamId }) => {
  const [sensorValue, setSensorValue] = React.useState(null);
  
  React.useEffect(() => {
    if (!streamId) return;
    const [moduleId, streamName] = streamId.split('.');
    
    const updateInterval = setInterval(() => {
      if (window.GlobalData?.data?.[moduleId]?.streams?.[streamName]) {
        setSensorValue(window.GlobalData.data[moduleId].streams[streamName].value);
      }
    }, 100);
    return () => clearInterval(updateInterval);
  }, [streamId]);

  return React.createElement(
    'div',
    { className: 'graph-display' },
    React.createElement('h3', null, 'Graph Display'),
    React.createElement('p', null, `Monitoring Stream: ${streamId}`),
    React.createElement('p', null, `Current Value: ${sensorValue !== null ? sensorValue : 'No data'}`)
  );
};

export default GraphDisplay;