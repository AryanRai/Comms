from socketify import App, OpCode, CompressOptions
import json

# Simulated active streams (in a real scenario, this would be dynamically populated)
active_streams = []

# Function called when a new WebSocket connection is opened
def ws_open(ws):
    print("A WebSocket connected!")
    # Subscribe the client to the 'broadcast' topic
    ws.subscribe("broadcast")

# Function called when a message is received from a client
def ws_message(ws, message, opcode):
    print(f"Received message: {message}")
    global active_streams
    # Parse the received message (assuming it's in JSON format)
    try:
        data = json.loads(message)
        
        
        # If the client sends a query for active streams
        if data.get('type') == 'query' and data.get('query_type') == 'active_streams':
            response = {
                'type': 'active_streams',
                'streams': active_streams  # Sending the active streams back to the client
            }
            ws.send(json.dumps(response), OpCode.TEXT)
            print("Sent active streams to client.")

        elif data.get('type') == 'negotiation':
            active_streams = data["data"]
            ws.publish("broadcast", message, opcode)

        else:
            # If it's a normal message, broadcast it to all clients
            ws.publish("broadcast", message, opcode)
    except json.JSONDecodeError:
        print("Error decoding JSON.")

# WebSocket server setup
app = App()
app.ws(
    "/*",  # Listen on all routes
    {
        "compression": CompressOptions.SHARED_COMPRESSOR,
        "max_payload_length": 16 * 1024 * 1024,  # 16MB payload limit
        "idle_timeout": 60,
        "open": ws_open,
        "message": ws_message,
        "close": lambda ws, code, message: print(f"WebSocket closed with code {code}"),
    }
)
app.any("/", lambda res, req: res.end("Nothing to see here!"))
app.listen(3000, lambda config: print("Listening on http://localhost:3000"))
app.run()
