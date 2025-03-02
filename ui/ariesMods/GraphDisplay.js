// ui/ariesMods/GraphDisplay.js
console.log('importing GraphDisplay');
const GraphDisplay = ({ streamId }) => {
  const [dataPoints, setDataPoints] = React.useState([]);

  const loadChartJs = () => {
    return new Promise((resolve, reject) => {
      if (window.Chart) {
        console.log('Chart.js already loaded');
        resolve(window.Chart);
        return;
      }

      console.log('Fetching Chart.js...');
      fetch('https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.min.js')
        .then(response => {
          if (!response.ok) throw new Error(`Failed to fetch Chart.js: ${response.status}`);
          return response.text();
        })
        .then(scriptText => {
          const script = document.createElement('script');
          script.text = scriptText;
          document.head.appendChild(script);
          console.log('Chart.js script injected');
          const checkInterval = setInterval(() => {
            if (window.Chart) {
              console.log('Chart.js detected');
              clearInterval(checkInterval);
              resolve(window.Chart);
            }
          }, 50);
        })
        .catch(error => {
          console.error('Failed to load Chart.js:', error);
          reject(error);
        });
    });
  };

  let chartInstance = null;
  let chartContainer;

  React.useEffect(() => {
    if (!streamId) {
      console.log('No streamId provided');
      return;
    }
    const [moduleId, streamName] = streamId.split('.');
    console.log('Stream ID:', { moduleId, streamName });

    // Create chart container
    chartContainer = document.createElement('div');
    chartContainer.id = `chart-${streamId.replace('.', '-')}`;
    chartContainer.style.width = '100%';
    chartContainer.style.height = '300px';
    chartContainer.style.background = '#f0f0f0'; // Debugging visibility
    const canvas = document.createElement('canvas');
    chartContainer.appendChild(canvas);
    console.log('Chart container created:', chartContainer.id);

    const initChart = async () => {
      try {
        const Chart = await loadChartJs();
        console.log('Chart.js loaded');

        const ctx = canvas.getContext('2d');
        if (!ctx) throw new Error('Failed to get 2D context');
        chartInstance = new Chart(ctx, {
          type: 'line',
          data: {
            labels: [],
            datasets: [{
              label: `Stream: ${streamId}`,
              data: [],
              borderColor: 'rgba(75, 192, 192, 1)',
              backgroundColor: 'rgba(75, 192, 192, 0.2)',
              fill: false
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
              x: { title: { display: true, text: 'Time' } },
              y: { title: { display: true, text: 'Value' } }
            }
          }
        });
        console.log('Chart initialized');

        // Test with static data
        chartInstance.data.labels = ['Test1', 'Test2', 'Test3'];
        chartInstance.data.datasets[0].data = [10, 20, 30];
        chartInstance.update();
        console.log('Test data added');

        const updateInterval = setInterval(() => {
          const streamData = window.GlobalData?.data?.[moduleId]?.streams?.[streamName];
          if (streamData) {
            const newValue = streamData.value;
            console.log(`New value for ${streamId}:`, newValue);
            setDataPoints(prev => {
              const now = new Date().toLocaleTimeString();
              const updatedPoints = [...prev, { x: now, y: newValue }].slice(-50);
              chartInstance.data.labels = updatedPoints.map(p => p.x);
              chartInstance.data.datasets[0].data = updatedPoints.map(p => p.y);
              chartInstance.update();
              console.log('Chart updated:', updatedPoints.length);
              return updatedPoints;
            });
          } else {
            console.log(`No data for ${streamId}`);
          }
        }, 100);

        return () => {
          clearInterval(updateInterval);
          if (chartInstance) chartInstance.destroy();
          console.log('Cleanup complete');
        };
      } catch (error) {
        console.error('Chart init error:', error);
        chartContainer.textContent = 'Chart failed to load';
      }
    };

    initChart();
    // Explicitly append to DOM
    const root = document.getElementById('root');
    if (root) {
      root.appendChild(chartContainer);
      console.log('Container appended to #root');
    } else {
      console.error('Root element not found');
    }

    return () => {
      if (chartContainer && chartContainer.parentNode) {
        chartContainer.parentNode.removeChild(chartContainer);
      }
    };
  }, [streamId]);

  return React.createElement(
    'div',
    { className: 'graph-display' },
    chartContainer || React.createElement('div', null, 'Loading...')
  );
};

export default GraphDisplay;