// index.js
export default {
    name: "plotly-graph-widget",
    displayName: "Real-Time Plotly Graph",
    description: "A widget for displaying real-time data using Plotly.",
    
    // Load Plotly CDN
    async initialize() {
      if (!window.Plotly) {
        const script = document.createElement('script');
        script.src = "https://cdn.plot.ly/plotly-latest.min.js";
        script.async = true;
        script.onload = () => console.log("Plotly loaded");
        document.head.appendChild(script);
      }
    },
  
    // Define the React component
    component: () => import('./PlotlyGraph'),
  };
  