from socketify import App, OpCode, CompressOptions

# Function called when a new WebSocket connection is opened
def ws_open(ws):
    print("A WebSocket connected!")
    # Subscribe the client to the 'broadcast' topic
    ws.subscribe("broadcast")

# Function called when a message is received from a client
def ws_message(ws, message, opcode):
    print(f"Received message: {message}")
    # Publish the received message to all clients subscribed to 'broadcast'
    ws.publish("broadcast", message, opcode)

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
