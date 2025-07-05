let ws;
let reconnectInterval = 5000; // Time to wait before reconnecting
let isConnected = false;
let ReconnBool = true;

// Add GlobalData to window object so it's accessible everywhere
window.GlobalData = {
  data: {} // Initialize with empty data object
};

// Start function to initialize WebSocket
function startWebSocket() {
  ws = new WebSocket('ws://localhost:3000');
  
  ws.onopen = () => {
    console.log('ITF: Connected to WebSocket server');
    isConnected = true;
    update_app_scoll_status("ITF: Connected to WebSocket server", NaN);
    update_SH_live_status("LINK", "success");
    // Query active streams upon connection
    queryActiveStreams();
    
    // Start subscribing to streams
    //subscribeToStreams();
  };

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (Debuglvl > 2) {
      console.log('ITF: Received:', data);
    } 

    // Handle received data
    handleReceivedData(data);
  };

  ws.onerror = (error) => {
    console.error('ITF: WebSocket error:', error);
    update_app_scoll_status("ITF: error occurred", NaN);
  };

  ws.onclose = () => {
    console.log('ITF: WebSocket connection closed');
    isConnected = false;
    update_app_scoll_status("ITF: disconnected", NaN);
    pingServer();
    // Attempt to reconnect after a delay
    setTimeout(reconnectWebSocket, reconnectInterval);
  };
}

// Reconnect function in case the connection is lost
function reconnectWebSocket() {
  if (!isConnected && ReconnBool) {
    console.log('ITF: Attempting to reconnect...');
    update_app_scoll_status("ITF: Reconnecting", NaN);
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
    console.log('ITF: Query for active streams sent');
  }
}

// Function to subscribe to specific streams
function subscribeToStreams() {
  // Example: Send a subscription message
  const subscribeMessage = JSON.stringify({
    type: "subscribe",
    stream_id: "stream_1" // Specify the stream you want to subscribe to
  });
  if (ws.readyState === WebSocket.OPEN) {
    ws.send(subscribeMessage);
    console.log('ITF: Subscribed to stream:', "stream_1");
  }
  
  // You can implement subscriptions to other streams here as needed
}

// Handle the received data from the WebSocket server
function handleReceivedData(data) {
  if (data.type === "active_streams") {
    // Handle the active streams received from the server
    console.log("ITF: Active streams:", data.data);
    // Process and update the UI with active streams information
    update_app_stream_list(data.data);
  } 
  
  else if (data.type === "negotiation") {
    // Handle stream update data
    if (Debuglvl > 2) {
      console.log("ITF: Stream update received:", data);
    }
    update_app_scoll_status("ITF: Recieved Broadcast", NaN);
    window.GlobalData = data; // Update the global reference
    // Update the UI with new stream values
  }

  else if (data.type === "update") {
    // Handle stream update data
    if (Debuglvl > 2) {
      console.log("ITF: Stream update received:", data);
    }
    
    update_app_scoll_status("ITF: Recieved Broadcast", NaN);
    // Update the UI with new stream values
  }

  else if (data.type === "control_response") {
    console.log("ITF: Control response received:", data);
    update_app_scoll_status(`ITF: Control response from ${data.module_id}: ${data.status}`, NaN);
  }

  else if (data.type === "config_response") {
    console.log("ITF: Config update response received:", data);
    update_app_scoll_status(`ITF: Config response from ${data.module_id}: ${data.status}`, NaN);
  }
}

// Function to check if the WebSocket server is alive without connecting
function pingServer() {

  if (isConnected) {
    console.log("ITF: Already connected to the server");
    update_SH_live_status("LINK", "success");
  }

  else {
  // Use fetch to ping the server
  fetch('http://localhost:3000') // Assuming WebSocket server also responds to HTTP requests
    .then(response => {
      if (response.ok) {
        console.log("ITF: Server is alive");
        update_app_scoll_status("ITF: Server is alive", NaN);
        update_SH_live_status("LIVE", "warning");
      } else {
        console.log("ITF: Server is not reachable, status code:", response.status);
        update_app_scoll_status(`ITF: Server is not reachable, status code: ${response.status}`, NaN);
        update_SH_live_status("Dead", "danger");
      }
    })
    .catch(error => {
      console.log("ITF: Failed to ping the server", error);
      update_app_scoll_status("ITF: Failed to ping the server", NaN);
      update_SH_live_status("Dead", "danger");
    });
  }
}

// Close function to gracefully close the WebSocket connection
function closeWebSocket() {
  if (ws && isConnected) {
    ws.close();
    update_app_scoll_status("ITF: WebSocket connection closed manually", NaN);
    console.log('ITF: WebSocket connection closed manually');
  }
}

// Start the WebSocket connection initially
//startWebSocket();

// Function to send control command to a module
function sendModuleControl(moduleId, command) {
  if (ws.readyState === WebSocket.OPEN) {
    const controlMessage = JSON.stringify({
      type: "control",
      module_id: moduleId,
      command: command
    });
    ws.send(controlMessage);
    console.log('ITF: Sent control command to module:', moduleId, command);
    update_app_scoll_status(`ITF: Sent control command to ${moduleId}`, NaN);
  }
}

// Function to update module configuration
function updateModuleConfig(moduleId, configUpdates) {
  if (ws.readyState === WebSocket.OPEN) {
    const configMessage = JSON.stringify({
      type: "config_update",
      module_id: moduleId,
      config: configUpdates
    });
    ws.send(configMessage);
    console.log('ITF: Sent config update to module:', moduleId, configUpdates);
    update_app_scoll_status(`ITF: Sent config update to ${moduleId}`, NaN);
  }
}

// Add to window object for global access
window.sendModuleControl = sendModuleControl;
window.updateModuleConfig = updateModuleConfig;


