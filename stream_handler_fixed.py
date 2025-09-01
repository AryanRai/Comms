#!/usr/bin/env python3
"""
Stream Handler v4.0 - Fixed Version
Fixed the async event loop issue for Windows compatibility
"""

from socketify import App, OpCode, CompressOptions
import json
import logging
import sys
import os
import time
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Global state
connected_clients = set()
active_streams = {}

def ws_open(ws):
    """Handle new WebSocket connection"""
    logger.info("New WebSocket connection established")
    connected_clients.add(ws)
    
    # Subscribe to all channels
    ws.subscribe("broadcast")
    ws.subscribe("physics")
    ws.subscribe("tools")
    
    # Send welcome message
    welcome_message = {
        "type": "system_info",
        "message": "Connected to Stream Handler v4.0 (Fixed)",
        "version": "4.0-fixed",
        "features": {
            "tool_execution": True,
            "physics_simulation": True,
            "ally_integration": True,
            "chyappy_protocol": "3.0"
        },
        "timestamp": datetime.now().isoformat()
    }
    
    ws.send(json.dumps(welcome_message), OpCode.TEXT)
    
    # Send initial ping
    ws.send(json.dumps({
        'type': 'ping',
        'timestamp': time.time(),
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
    
    print(f"\n=== STREAM HANDLER v4.0 FIXED DEBUG ===")
    print(f"[RECEIVED] Raw message: {message}")
    print(f"[RECEIVED] Message length: {len(message)} characters")
    
    try:
        # Parse JSON message
        data = json.loads(message)
        message_type = data.get('type')
        
        if not message_type:
            logger.error("Message missing 'type' field")
            return
        
        print(f"[PARSED] Message type: {message_type}")
        logger.info(f"Processing message type: {message_type}")
        
        # Handle different message types
        if message_type == 'ping':
            handle_ping(ws, data, opcode)
        elif message_type == 'ally_intent':
            handle_ally_intent(ws, data, opcode)
        elif message_type == 'ally_status':
            handle_ally_status(ws, data, opcode)
        elif message_type == 'tool_call':
            handle_tool_call(ws, data, opcode)
        elif message_type == 'query':
            handle_query(ws, data, opcode)
        else:
            handle_unknown_message(ws, data, opcode)
            
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON received: {e}")
        send_error_response(ws, "INVALID_JSON", "Message is not valid JSON")
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        send_error_response(ws, "PROCESSING_ERROR", "Internal error processing message")
    finally:
        print(f"=== END STREAM HANDLER v4.0 FIXED DEBUG ===\n")

def handle_ping(ws, data, opcode):
    """Handle ping messages"""
    timestamp = data.get('timestamp')
    target = data.get('target', 'sh')
    
    if target == 'sh':
        response = {
            'type': 'pong',
            'timestamp': timestamp,
            'target': target,
            'server_time': time.time(),
            'status': 'active',
            'msg-sent-timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        ws.send(json.dumps(response), OpCode.TEXT)
        print(f"[PING] Responded to ping with pong")

def handle_ally_status(ws, data, opcode):
    """Handle Ally status messages"""
    status = data.get('status', '')
    component = data.get('component', '')
    details = data.get('details', {})
    print(f"[ALLY] Received status from {component}: {status}")
    print(f"[ALLY] Details: {details}")
    
    # Acknowledge the status
    response = {
        'type': 'ally_status',
        'status': 'acknowledged',
        'component': 'stream_handler_fixed',
        'details': {
            'received_from': component,
            'received_status': status,
            'acknowledged_at': datetime.now().isoformat()
        },
        'msg-sent-timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    ws.send(json.dumps(response), OpCode.TEXT)

def handle_ally_intent(ws, data, opcode):
    """Handle Ally intent messages"""
    intent = data.get('intent', '')
    print(f"[ALLY] Processing ally intent: {intent}")
    
    # Send acknowledgment
    response = {
        'type': 'ally_status',
        'status': 'processing',
        'component': 'stream_handler_fixed',
        'details': {
            'intent': intent,
            'received_at': datetime.now().isoformat()
        },
        'msg-sent-timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    ws.send(json.dumps(response), OpCode.TEXT)
    
    # Simulate tool execution for calculator
    if 'calculate' in intent.lower() or any(op in intent for op in ['+', '-', '*', '/']):
        simulate_calculator_tool(ws, intent)
    else:
        # Send completion status
        completion_response = {
            'type': 'ally_status',
            'status': 'completed',
            'component': 'stream_handler_fixed',
            'details': {
                'intent': intent,
                'result': f"Processed intent: {intent}",
                'completed_at': datetime.now().isoformat()
            },
            'msg-sent-timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        ws.send(json.dumps(completion_response), OpCode.TEXT)

def simulate_calculator_tool(ws, intent):
    """Simulate calculator tool execution"""
    print(f"[TOOL] Simulating calculator for: {intent}")
    
    # Send tool_call message
    tool_call = {
        'type': 'tool_call',
        'tool_name': 'calculator',
        'parameters': {'expression': intent},
        'execution_id': f"calc_{int(time.time())}",
        'context': {
            'conversationId': 'test_conversation',
            'sessionId': 'test_session'
        },
        'msg-sent-timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    ws.send(json.dumps(tool_call), OpCode.TEXT)
    
    # Simulate calculation
    try:
        # Simple expression evaluation (unsafe but for demo)
        import re
        numbers = re.findall(r'\d+', intent)
        if len(numbers) >= 2:
            if '+' in intent:
                result = int(numbers[0]) + int(numbers[1])
            elif '-' in intent:
                result = int(numbers[0]) - int(numbers[1])
            elif '*' in intent:
                result = int(numbers[0]) * int(numbers[1])
            elif '/' in intent:
                result = int(numbers[0]) / int(numbers[1])
            else:
                result = "Could not parse expression"
        else:
            result = "Invalid expression"
    except:
        result = "Calculation error"
    
    # Send tool_result message
    tool_result = {
        'type': 'tool_result',
        'execution_id': tool_call['execution_id'],
        'tool_name': 'calculator',
        'status': 'success',
        'result': {'answer': result},
        'execution_info': {
            'start_time': datetime.now().isoformat(),
            'end_time': datetime.now().isoformat(),
            'duration_ms': 100
        },
        'msg-sent-timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    ws.send(json.dumps(tool_result), OpCode.TEXT)
    print(f"[TOOL] Calculator result: {result}")

def handle_tool_call(ws, data, opcode):
    """Handle tool call messages"""
    tool_name = data.get('tool_name')
    print(f"[TOOL] Processing tool call: {tool_name}")
    
    # Echo back as processed
    response = {
        'type': 'tool_result',
        'execution_id': data.get('execution_id', 'unknown'),
        'tool_name': tool_name,
        'status': 'success',
        'result': {'message': f'Tool {tool_name} executed successfully'},
        'msg-sent-timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    ws.send(json.dumps(response), OpCode.TEXT)

def handle_query(ws, data, opcode):
    """Handle query messages"""
    query_type = data.get('query_type')
    
    if query_type == 'active_streams':
        response = {
            'type': 'active_streams',
            'data': active_streams,
            'timestamp': time.time()
        }
        ws.send(json.dumps(response), OpCode.TEXT)
    else:
        # Echo back unknown queries
        response = {
            'type': 'query_response',
            'query_type': query_type,
            'status': 'unknown_query',
            'msg-sent-timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        ws.send(json.dumps(response), OpCode.TEXT)

def handle_unknown_message(ws, data, opcode):
    """Handle unknown message types"""
    message_type = data.get('type')
    logger.warning(f"Unknown message type: {message_type}")
    
    # Echo back
    response = {
        'type': 'echo',
        'original_type': message_type,
        'original_message': data,
        'status': 'received',
        'msg-sent-timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    ws.send(json.dumps(response), OpCode.TEXT)

def send_error_response(ws, error_code, error_message):
    """Send error response to client"""
    error_response = {
        "type": "error",
        "error": {
            "code": error_code,
            "message": error_message
        },
        "timestamp": time.time()
    }
    ws.send(json.dumps(error_response), OpCode.TEXT)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Stream Handler v4.0 - Fixed Version")
    parser.add_argument("--port", type=int, default=3000, help="Port to listen on")
    args = parser.parse_args()
    
    print("=" * 80)
    print("Stream Handler v4.0 - Fixed Version")
    print("Tool Calling Framework + Physics Simulation + Ally Integration")
    print("Fixed async event loop for Windows compatibility")
    print("=" * 80)
    
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
    app.any("/", lambda res, req: res.end("Stream Handler v4.0 - Fixed Version"))
    app.any("/status", lambda res, req: res.end(json.dumps({
        "status": "active",
        "version": "4.0-fixed",
        "connections": len(connected_clients),
        "tool_support": True,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })))
    
    logger.info(f"Starting Stream Handler v4.0 (Fixed) on port {args.port}")
    app.listen(args.port, lambda config: logger.info(f"Listening on http://localhost:{args.port}"))
    
    # Run the server (this blocks and handles the event loop properly)
    app.run()