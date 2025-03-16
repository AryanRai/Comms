// ui/ariesMods/GraphDisplay.js
// Simple logging utility
const LogLevels = {
  DEBUG: 0,
  INFO: 1,
  WARN: 2,
  ERROR: 3
};

const log = (level, message, ...args) => {
  const currentLevel = window.DEBUG_LEVEL || LogLevels.INFO; // Default to INFO
  if (level >= currentLevel) {
    const prefix = `[${Object.keys(LogLevels)[level]}]`;
    switch (level) {
      case LogLevels.DEBUG:
        console.debug(prefix, message, ...args);
        break;
      case LogLevels.INFO:
        console.info(prefix, message, ...args);
        break;
      case LogLevels.WARN:
        console.warn(prefix, message, ...args);
        break;
      case LogLevels.ERROR:
        console.error(prefix, message, ...args);
        break;
    }
  }
};

log(LogLevels.INFO, 'importing GraphDisplay');

const GraphDisplay = ({ streamId }) => {
  const [dataPoints, setDataPoints] = React.useState([]);
  const plotDivRef = React.useRef(null);

  const loadPlotly = () => {
    return new Promise((resolve, reject) => {
      if (window.Plotly) {
        log(LogLevels.DEBUG, 'Plotly already loaded');
        resolve(window.Plotly);
        return;
      }
      log(LogLevels.INFO, 'Fetching Plotly...');
      fetch('https://cdn.plot.ly/plotly-latest.min.js')
        .then(response => response.text())
        .then(scriptText => {
          const script = document.createElement('script');
          script.text = scriptText;
          document.head.appendChild(script);
          log(LogLevels.DEBUG, 'Plotly injected');
          const check = setInterval(() => {
            if (window.Plotly) {
              log(LogLevels.DEBUG, 'Plotly ready');
              clearInterval(check);
              resolve(window.Plotly);
            }
          }, 50);
        })
        .catch(error => {
          log(LogLevels.ERROR, 'Plotly load failed:', error);
          reject(error);
        });
    });
  };

  React.useEffect(() => {
    if (!streamId || !plotDivRef.current) {
      log(LogLevels.WARN, 'Missing streamId or plotDivRef');
      return;
    }
    const [moduleId, streamName] = streamId.split('.');
    log(LogLevels.DEBUG, 'Stream:', { moduleId, streamName });

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
        log(LogLevels.INFO, 'Plot initialized');

        Plotly.update(plotDiv, { x: [['Start']], y: [[0]] }, [0]);

        const updateInterval = setInterval(() => {
          const value = window.GlobalData?.data?.[moduleId]?.streams?.[streamName]?.value;
          if (value !== undefined) {
            log(LogLevels.DEBUG, `Value for ${streamId}:`, value);
            setDataPoints(prev => {
              const now = new Date().toLocaleTimeString();
              const updated = [...prev, { x: now, y: value }].slice(-50);
              Plotly.update(plotDiv, {
                x: [updated.map(p => p.x)],
                y: [updated.map(p => p.y)]
              }, [0]);
              log(LogLevels.DEBUG, 'Plot updated');
              return updated;
            });
          } else {
            log(LogLevels.WARN, `No data for ${streamId}`);
          }
        }, 100);

        return () => {
          clearInterval(updateInterval);
          log(LogLevels.DEBUG, 'Update interval cleared');
        };
      } catch (error) {
        log(LogLevels.ERROR, 'Plot init error:', error);
        plotDiv.textContent = 'Plot error';
      }
    };

    initPlot();
  }, [streamId]);

  return React.createElement(
    'div',
    { className: 'graph-display' },
    React.createElement('div', { ref: plotDivRef, id: `plot-${streamId ? streamId.replace('.', '-') : 'default'}` })
  );
};

export default GraphDisplay;