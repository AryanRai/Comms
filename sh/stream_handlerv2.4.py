"""
Enhanced Stream Handler v2.4 with tool message routing support.
Extends the existing Chyappy v3.0 protocol with tool_call and tool_result message handling.
"""

from socketify import App, OpCode, CompressOptions
import json
import asyncio
import logging
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from tool_message_handlers import route_tool_message, start_tool_handlers, stop_tool_handlers
from message_validation import deserialize_message, MessageValidationError
from message_registry import get_registry

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Global state
active_streams = []
connected_clients = set()
message_registry = get_registry()
tool_handlers_started = False


class EnhancedStreamHandler:
    """Enhanced stream handler with tool message support"""
    
    def __init__(self, port: int = 3000):
        """Initialize the enhanced stream handler"""
        self.port = port
        self.app = None
        self.running = False
        
    async def start(self):
        """Start the stream handler and tool message handlers"""
        global tool_handlers_started
        
        if not tool_handlers_started:
            await start_tool_handlers()
            tool_handlers_started = True
            logger.info("Tool message handlers started")
        
        # Set up WebSocket server
        self.app = App()
        self.app.ws(
            "/*",
            {
                "compression": CompressOptions.SHARED_COMPRESSOR,
                "max_payload_length": 16 * 1024 * 1024,  # 16MB payload limit
                "idle_timeout": 60,
                "open": self.ws_open,
                "message": self.ws_message,
                "close": self.ws_close,
            }
        )
        self.app.any("/", lambda res, req: res.end("Chyappy v3.0 Stream Handler with Tool Support"))
        
        logger.info(f"Starting Enhanced Stream Handler on port {self.port}")
        self.app.listen(self.port, lambda config: logger.info(f"Listening on http://localhost:{self.port}"))
        self.running = True
        
        # Run the server
        self.app.run()
    
    async def stop(self):
        """Stop the stream handler and tool message handlers"""
        global tool_handlers_started
        
        self.running = False
        
        if tool_handlers_started:
            await stop_tool_handlers()
            tool_handlers_started = False
            logger.info("Tool message handlers stopped")
        
        logger.info("Enhanced Stream Handler stopped")
    
    def ws_open(self, ws):
        """Handle new WebSocket connection"""
        logger.info("New WebSocket connection established")
        connected_clients.add(ws)
        
        # Subscribe to broadcast topic
        ws.subscribe("broadcast")
        
        # Send welcome message with supported message types
        welcome_message = {
            "type": "system_info",
            "message": "Connected to Chyappy v3.0 with Tool Support",
            "supported_message_types": message_registry.list_types(),
            "tool_execution_enabled": True,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        ws.send(json.dumps(welcome_message), OpCode.TEXT)
    
    def ws_close(self, ws, code, message):
        """Handle WebSocket connection close"""
        logger.info(f"WebSocket connection closed with code {code}")
        connected_clients.discard(ws)
    
    def ws_message(self, ws, message, opcode):
        """Handle incoming WebSocket message"""
        logger.debug(f"Received message: {message}")
        
        # Create async task to handle the message
        asyncio.create_task(self.handle_message_async(ws, message, opcode))
    
    async def handle_message_async(self, ws, message_str, opcode):
        """Handle message asynchronously"""
        global active_streams
        
        try:
            # Parse JSON message
            try:
                message = json.loads(message_str)
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON received: {e}")
                await self.send_error_response(ws, "INVALID_JSON", "Message is not valid JSON")
                return
            
            # Validate message has type field
            message_type = message.get('type')
            if not message_type:
                logger.error("Message missing 'type' field")
                await self.send_error_response(ws, "MISSING_TYPE", "Message must have a 'type' field")
                return
            
            logger.info(f"Processing message type: {message_type}")
            
            # Handle different message types
            if message_type in ['tool_call', 'tool_result']:
                # Route tool messages to tool handlers
                success = await route_tool_message(
                    message, 
                    lambda msg: self.broadcast_message(msg, opcode)
                )
                
                if not success:
                    await self.send_error_response(
                        ws, "TOOL_HANDLER_ERROR", 
                        f"Failed to handle {message_type} message"
                    )
                
            elif message_type == 'query' and message.get('query_type') == 'active_streams':
                # Handle legacy active streams query
                response = {
                    'type': 'active_streams',
                    'data': active_streams,
                    'timestamp': asyncio.get_event_loop().time()
                }
                ws.send(json.dumps(response), OpCode.TEXT)
                logger.info("Sent active streams to client")
                
            elif message_type == 'ally_query':
                # Handle ally query messages
                await self.handle_ally_query(ws, message, opcode)
                
            elif message_type == 'negotiation':
                # Handle legacy negotiation messages
                active_streams = message.get("data", [])
                self.broadcast_message(message_str, opcode)
                logger.info("Processed negotiation message")
                
            elif message_type in ['ally_intent', 'ally_memory', 'ally_status']:
                # Handle other ally messages by broadcasting
                self.broadcast_message(message_str, opcode)
                logger.info(f"Broadcasted {message_type} message")
                
            else:
                # Handle unknown or legacy message types
                logger.warning(f"Unknown message type: {message_type}")
                
                # Check if it's a deprecated type
                if message_registry.is_deprecated(message_type):
                    replacement = message_registry.get_replacement_type(message_type)
                    warning_msg = f"Message type '{message_type}' is deprecated"
                    if replacement:
                        warning_msg += f", use '{replacement}' instead"
                    
                    await self.send_warning_response(ws, "DEPRECATED_MESSAGE_TYPE", warning_msg)
                
                # Broadcast anyway for backward compatibility
                self.broadcast_message(message_str, opcode)
                
        except MessageValidationError as e:
            logger.error(f"Message validation error: {e}")
            await self.send_error_response(ws, "VALIDATION_ERROR", str(e))
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await self.send_error_response(ws, "PROCESSING_ERROR", "Internal error processing message")
    
    async def handle_ally_query(self, ws, message, opcode):
        """Handle ally_query messages"""
        query_type = message.get('query_type')
        
        if query_type == 'active_streams':
            response = {
                'type': 'ally_query',
                'query_type': 'active_streams',
                'response_data': {
                    'streams': active_streams,
                    'count': len(active_streams)
                },
                'msg-sent-timestamp': asyncio.get_event_loop().time()
            }
            ws.send(json.dumps(response), OpCode.TEXT)
            
        elif query_type == 'system_status':
            response = {
                'type': 'ally_query',
                'query_type': 'system_status',
                'response_data': {
                    'status': 'online',
                    'connected_clients': len(connected_clients),
                    'active_streams': len(active_streams),
                    'tool_support': True,
                    'supported_message_types': message_registry.list_types()
                },
                'msg-sent-timestamp': asyncio.get_event_loop().time()
            }
            ws.send(json.dumps(response), OpCode.TEXT)
            
        else:
            # Broadcast query to other components
            self.broadcast_message(json.dumps(message), opcode)
    
    def broadcast_message(self, message_str, opcode):
        """Broadcast message to all connected clients"""
        try:
            # Use the app's publish method to broadcast
            if self.app:
                self.app.publish("broadcast", message_str, opcode)
                logger.debug("Message broadcasted to all clients")
        except Exception as e:
            logger.error(f"Error broadcasting message: {e}")
    
    async def send_error_response(self, ws, error_code: str, error_message: str):
        """Send error response to client"""
        error_response = {
            "type": "error",
            "error": {
                "code": error_code,
                "message": error_message
            },
            "timestamp": asyncio.get_event_loop().time()
        }
        
        try:
            ws.send(json.dumps(error_response), OpCode.TEXT)
        except Exception as e:
            logger.error(f"Failed to send error response: {e}")
    
    async def send_warning_response(self, ws, warning_code: str, warning_message: str):
        """Send warning response to client"""
        warning_response = {
            "type": "warning",
            "warning": {
                "code": warning_code,
                "message": warning_message
            },
            "timestamp": asyncio.get_event_loop().time()
        }
        
        try:
            ws.send(json.dumps(warning_response), OpCode.TEXT)
        except Exception as e:
            logger.error(f"Failed to send warning response: {e}")


# Legacy compatibility functions for existing code
def ws_open(ws):
    """Legacy WebSocket open handler"""
    logger.info("A WebSocket connected!")
    connected_clients.add(ws)
    ws.subscribe("broadcast")

def ws_message(ws, message, opcode):
    """Legacy WebSocket message handler"""
    logger.debug(f"Received message: {message}")
    
    # Create handler instance and process message
    handler = EnhancedStreamHandler()
    asyncio.create_task(handler.handle_message_async(ws, message, opcode))

def ws_close(ws, code, message):
    """Legacy WebSocket close handler"""
    logger.info(f"WebSocket closed with code {code}")
    connected_clients.discard(ws)


# Main execution for backward compatibility
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Enhanced Stream Handler v2.4")
    parser.add_argument("--port", type=int, default=3000, help="Port to listen on")
    parser.add_argument("--legacy", action="store_true", help="Run in legacy compatibility mode")
    args = parser.parse_args()
    
    if args.legacy:
        # Legacy mode - use original structure
        logger.info("Running in legacy compatibility mode")
        
        app = App()
        app.ws(
            "/*",
            {
                "compression": CompressOptions.SHARED_COMPRESSOR,
                "max_payload_length": 16 * 1024 * 1024,
                "idle_timeout": 60,
                "open": ws_open,
                "message": ws_message,
                "close": ws_close,
            }
        )
        app.any("/", lambda res, req: res.end("Chyappy v3.0 Stream Handler (Legacy Mode)"))
        app.listen(args.port, lambda config: logger.info(f"Listening on http://localhost:{args.port}"))
        app.run()
    else:
        # Enhanced mode - use new handler class
        logger.info("Running in enhanced mode with tool support")
        
        async def main():
            handler = EnhancedStreamHandler(args.port)
            try:
                await handler.start()
            except KeyboardInterrupt:
                logger.info("Received interrupt signal")
            finally:
                await handler.stop()
        
        asyncio.run(main())