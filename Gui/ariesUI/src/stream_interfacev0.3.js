let ws;
let reconnectInterval = 5000; // Time to wait before reconnecting
let isConnected = false;

// Start function to initialize WebSocket
function startWebSocket() {
  ws = new WebSocket('ws://localhost:3000');
  
  ws.onopen = () => {
    console.log('Connected to WebSocket server');
    isConnected = true;
    update_app_scoll_status("Connected to WebSocket server", NaN);

    // Query active streams upon connection
    queryActiveStreams();
    
    // Start subscribing to streams
    subscribeToStreams();
  };

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Received:', data);

    // Handle received data
    handleReceivedData(data);
  };

  ws.onerror = (error) => {
    console.error('WebSocket error:', error);
    update_app_unit_status("WebSocket error occurred", NaN);
  };

  ws.onclose = () => {
    console.log('WebSocket connection closed');
    isConnected = false;
    update_app_unit_status("WebSocket disconnected", NaN);

    // Attempt to reconnect after a delay
    setTimeout(reconnectWebSocket, reconnectInterval);
  };
}

// Reconnect function in case the connection is lost
function reconnectWebSocket() {
  if (!isConnected) {
    console.log('Attempting to reconnect...');
    startWebSocket();
  }
}

// Function to query active streams from the WebSocket server
function queryActiveStreams() {
  if (ws.readyState === WebSocket.OPEN) {
    const queryMessage = JSON.stringify({
      type: "query",
      query_type: "active_streams"
    });
    ws.send(queryMessage);
    console.log('Query for active streams sent');
  }
}

// Function to subscribe to specific streams
function subscribeToStreams() {
  // Example: Send a subscription message
  const subscribeMessage = JSON.stringify({
    type: "subscribe",
    stream_id: "temperature_stream" // Specify the stream you want to subscribe to
  });
  if (ws.readyState === WebSocket.OPEN) {
    ws.send(subscribeMessage);
    console.log('Subscribed to stream:', "temperature_stream");
  }
  
  // You can implement subscriptions to other streams here as needed
}

// Handle the received data from the WebSocket server
function handleReceivedData(data) {
  if (data.type === "active_streams") {
    // Handle the active streams received from the server
    console.log("Active streams:", data.streams);
    // Process and update the UI with active streams information
  } else if (data.type === "update") {
    // Handle stream update data
    console.log("Stream update received:", data);
    // Update the UI with new stream values
  }
}

// Close function to gracefully close the WebSocket connection
function closeWebSocket() {
  if (ws && isConnected) {
    ws.close();
    console.log('WebSocket connection closed manually');
  }
}

// Start the WebSocket connection initially
startWebSocket();

// Example: Button to close the WebSocket connection
document.getElementById('closeButton').addEventListener('click', () => {
  closeWebSocket();
});
