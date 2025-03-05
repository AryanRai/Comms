// ui/ariesMods/GraphDisplay.js
console.log('importing GraphDisplay');
const GraphDisplay = ({ streamId }) => {
  const [dataPoints, setDataPoints] = React.useState([]);
  const plotDivRef = React.useRef(null); // Use ref to persist the div

  const loadPlotly = () => {
    return new Promise((resolve, reject) => {
      if (window.Plotly) {
        console.log('Plotly already loaded');
        resolve(window.Plotly);
        return;
      }
      console.log('Fetching Plotly...');
      fetch('https://cdn.plot.ly/plotly-latest.min.js')
        .then(response => response.text())
        .then(scriptText => {
          const script = document.createElement('script');
          script.text = scriptText;
          document.head.appendChild(script);
          console.log('Plotly injected');
          const check = setInterval(() => {
            if (window.Plotly) {
              console.log('Plotly ready');
              clearInterval(check);
              resolve(window.Plotly);
            }
          }, 50);
        })
        .catch(error => {
          console.error('Plotly load failed:', error);
          reject(error);
        });
    });
  };

  React.useEffect(() => {
    if (!streamId || !plotDivRef.current) return;
    const [moduleId, streamName] = streamId.split('.');
    console.log('Stream:', { moduleId, streamName });

    const plotDiv = plotDivRef.current;
    plotDiv.style.width = '100%';
    plotDiv.style.height = '300px';

    const initPlot = async () => {
      try {
        const Plotly = await loadPlotly();
        const initialData = [{
          x: [],
          y: [],
          type: 'scatter',
          mode: 'lines+markers',
          name: streamId
        }];
        const layout = {
          title: `Stream: ${streamId}`,
          xaxis: { title: 'Time' },
          yaxis: { title: 'Value' }
        };
        Plotly.newPlot(plotDiv, initialData, layout);
        console.log('Plot initialized');

        Plotly.update(plotDiv, { x: [['Start']], y: [[0]] }, [0]);

        const updateInterval = setInterval(() => {
          const value = window.GlobalData?.data?.[moduleId]?.streams?.[streamName]?.value;
          if (value !== undefined) {
            console.log(`Value for ${streamId}:`, value);
            setDataPoints(prev => {
              const now = new Date().toLocaleTimeString();
              const updated = [...prev, { x: now, y: value }].slice(-50);
              Plotly.update(plotDiv, {
                x: [updated.map(p => p.x)],
                y: [updated.map(p => p.y)]
              }, [0]);
              console.log('Plot updated');
              return updated;
            });
          } else {
            console.log(`No data for ${streamId}`);
          }
        }, 100);

        return () => clearInterval(updateInterval);
      } catch (error) {
        console.error('Plot init error:', error);
        plotDiv.textContent = 'Plot error';
      }
    };

    initPlot();
  }, [streamId]);

  // Create the plot div once and reuse it
  return React.createElement(
    'div',
    { className: 'graph-display' },
    React.createElement('div', { ref: plotDivRef, id: `plot-${streamId ? streamId.replace('.', '-') : 'default'}` })
  );
};

export default GraphDisplay;