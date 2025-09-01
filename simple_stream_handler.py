#!/usr/bin/env python3
"""
Simple Stream Handler for testing WebSocket connections
Minimal implementation to verify Glass Chat integration
"""

from socketify import App, OpCode, CompressOptions
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Global state
connected_clients = set()

def ws_open(ws):
    """Handle new WebSocket connection"""
    logger.info("New WebSocket connection established")
    connected_clients.add(ws)
    
    # Subscribe to broadcast channel
    ws.subscribe("broadcast")
    
    # Send welcome message
    welcome_message = {
        "type": "system_info",
        "message": "Connected to Simple Stream Handler",
        "version": "4.0-simple",
        "features": {
            "tool_execution": True,
            "physics_simulation": False,
            "ally_integration": True
        },
        "timestamp": datetime.now().isoformat()
    }
    
    ws.send(json.dumps(welcome_message), OpCode.TEXT)
    
    # Send initial ping
    ws.send(json.dumps({
        'type': 'ping',
        'timestamp': datetime.now().timestamp(),
        'target': 'client',
        'status': 'active',
        'msg-sent-timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }), OpCode.TEXT)

def ws_close(ws, code, message):
    """Handle WebSocket connection close"""
    logger.info(f"WebSocket connection closed with code {code}")
    connected_clients.discard(ws)

def ws_message(ws, message, opcode):
    """Handle incoming WebSocket message"""
    logger.info(f"Received message: {message}")
    
    try:
        # Parse JSON message
        data = json.loads(message)
        message_type = data.get('type')
        
        logger.info(f"Processing message type: {message_type}")
        
        # Handle different message types
        if message_type == 'ping':
            # Respond to ping
            timestamp = data.get('timestamp')
            target = data.get('target', 'sh')
            
            if target == 'sh':
                response = {
                    'type': 'pong',
                    'timestamp': timestamp,
                    'target': target,
                    'server_time': datetime.now().timestamp(),
                    'status': 'active',
                    'msg-sent-timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                ws.send(json.dumps(response), OpCode.TEXT)
                
        elif message_type == 'ally_intent':
            # Handle Ally intent messages
            logger.info(f"Processing ally intent: {data.get('intent')}")
            
            # Echo back a response
            response = {
                'type': 'ally_status',
                'status': 'processed',
                'component': 'simple_stream_handler',
                'details': {
                    'intent': data.get('intent'),
                    'processed_at': datetime.now().isoformat()
                },
                'msg-sent-timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            ws.send(json.dumps(response), OpCode.TEXT)
            
            # Broadcast to other clients
            app.publish("broadcast", json.dumps(response), OpCode.TEXT)
            
        else:
            # Echo back unknown messages
            response = {
                'type': 'echo',
                'original_type': message_type,
                'original_message': data,
                'status': 'received',
                'msg-sent-timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            ws.send(json.dumps(response), OpCode.TEXT)
            
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON received: {e}")
        error_response = {
            "type": "error",
            "error": {
                "code": "INVALID_JSON",
                "message": "Message is not valid JSON"
            },
            "timestamp": datetime.now().timestamp()
        }
        ws.send(json.dumps(error_response), OpCode.TEXT)
        
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        error_response = {
            "type": "error",
            "error": {
                "code": "PROCESSING_ERROR",
                "message": "Internal error processing message"
            },
            "timestamp": datetime.now().timestamp()
        }
        ws.send(json.dumps(error_response), OpCode.TEXT)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Simple Stream Handler for testing")
    parser.add_argument("--port", type=int, default=3000, help="Port to listen on")
    args = parser.parse_args()
    
    print("=" * 60)
    print("Simple Stream Handler - WebSocket Testing")
    print("=" * 60)
    
    # Create the app
    app = App()
    
    # Set up WebSocket server
    app.ws(
        "/*",
        {
            "compression": CompressOptions.SHARED_COMPRESSOR,
            "max_payload_length": 16 * 1024 * 1024,  # 16MB payload limit
            "idle_timeout": 60,
            "open": ws_open,
            "message": ws_message,
            "close": ws_close,
        }
    )
    
    # HTTP routes
    app.any("/", lambda res, req: res.end("Simple Stream Handler - WebSocket Testing"))
    app.any("/status", lambda res, req: res.end(json.dumps({
        "status": "active",
        "version": "4.0-simple",
        "connections": len(connected_clients),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })))
    
    logger.info(f"Starting Simple Stream Handler on port {args.port}")
    app.listen(args.port, lambda config: logger.info(f"Listening on http://localhost:{args.port}"))
    
    # Run the server
    app.run()