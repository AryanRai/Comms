"""
Stream Handler v4.0 - Unified Protocol with Tool Calling and Physics Support
Merges capabilities from stream_handlerv2.4.py (tool calling) and stream_handlerv3.0_physics.py (physics simulation)
Extends Chyappy v3.0 protocol with comprehensive tool execution and physics simulation support.
"""

from socketify import App, OpCode, CompressOptions
import json
import asyncio
import logging
import sys
import os
import time
from datetime import datetime
import threading

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from tool_message_handlers import route_tool_message, start_tool_handlers, stop_tool_handlers
from message_validation import deserialize_message, MessageValidationError
from message_registry import get_registry

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
IDLE_TIMEOUT = 0.1  # Set WebSocket idle timeout to 100ms
DEBUG_REFRESH = 100  # Default debug refresh rate in ms
VERBOSE_LEVEL = 1  # Default verbose level (Debuglvl)

# Global state
active_streams = {}  # Dictionary format: {stream_id: stream_data}
physics_streams = {}  # Physics simulation streams
connected_clients = set()
message_registry = get_registry()
tool_handlers_started = False

# Chyappy protocol constants
CHYAPPY_V1_2_START = 0x7D
PAYLOAD_TYPE_STRING = 0x01
PAYLOAD_TYPE_FLOAT = 0x02
PAYLOAD_TYPE_INT16 = 0x03
PAYLOAD_TYPE_INT32 = 0x04

# Print banner
print("=" * 80)
print("Stream Handler v4.0 - Unified Protocol")
print("Tool Calling Framework + Physics Simulation + Ally Integration")
print("Chyappy v3.0 Protocol Compatible")
print("=" * 80)


class UnifiedStreamFormat:
    """
    Unified stream format compatible with both Chyappy protocol and WebSocket JSON.
    Maps Chyappy protocol concepts to WebSocket JSON for seamless integration.
    """
    
    @staticmethod
    def create_stream_data(stream_id, name, datatype, unit, value, status="active", 
                          sensor_type=None, sensor_id=None, sequence_number=None):
        """Create unified stream data format"""
        return {
            "stream_id": stream_id,
            "name": name,
            "datatype": datatype,  # float, int, string, etc.
            "unit": unit,
            "value": value,
            "status": status,
            "sensor_type": sensor_type,  # Chyappy sensor type (e.g., 'T', 'A', 'G')
            "sensor_id": sensor_id,      # Chyappy sensor ID (0-255)
            "sequence_number": sequence_number,  # Chyappy sequence number
            "timestamp": datetime.now().isoformat(),
            "payload_type": UnifiedStreamFormat.get_payload_type(datatype)
        }
    
    @staticmethod
    def get_payload_type(datatype):
        """Map datatype to Chyappy payload type"""
        mapping = {
            "string": PAYLOAD_TYPE_STRING,
            "float": PAYLOAD_TYPE_FLOAT,
            "int16": PAYLOAD_TYPE_INT16,
            "int32": PAYLOAD_TYPE_INT32,
            "int": PAYLOAD_TYPE_INT32
        }
        return mapping.get(datatype, PAYLOAD_TYPE_STRING)
    
    @staticmethod
    def create_negotiation_message(streams, msg_type="negotiation"):
        """Create unified negotiation message"""
        return {
            "type": msg_type,
            "status": "active",
            "data": streams,
            "msg-sent-timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    @staticmethod
    def create_physics_message(simulation_id, streams, command=None):
        """Create physics simulation message"""
        return {
            "type": "physics_simulation",
            "simulation_id": simulation_id,
            "command": command,
            "streams": streams,
            "status": "active",
            "msg-sent-timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    @staticmethod
    def create_trading_message(symbol, streams, market_data=None):
        """Create trading stream message"""
        return {
            "type": "trading_stream",
            "symbol": symbol,
            "streams": streams,
            "market_data": market_data,
            "status": "active",
            "msg-sent-timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }


class ConnectionManager:
    """Manages WebSocket connections with ping/pong and latency tracking"""
    
    def __init__(self):
        self.connections = {}  # WebSocket -> ConnectionInfo
        self.last_cleanup = time.time()
        
    def add_connection(self, ws):
        self.connections[ws] = {
            'connected_at': time.time(),
            'last_ping': time.time(),
            'last_pong': time.time(),
            'ping_interval': 0.1,  # 100ms ping interval
            'latency': 0,
            'status': 'connected'
        }
        
    def remove_connection(self, ws):
        if ws in self.connections:
            del self.connections[ws]
            
    def update_ping(self, ws, timestamp=None):
        if ws in self.connections:
            self.connections[ws]['last_ping'] = time.time()
            if timestamp:
                self.connections[ws]['ping_timestamp'] = timestamp
            
    def update_pong(self, ws, timestamp=None):
        if ws in self.connections:
            now = time.time()
            self.connections[ws]['last_pong'] = now
            if timestamp:
                try:
                    # Handle both millisecond and second timestamps
                    sent_time = float(timestamp)
                    if sent_time > 1000000000000:  # If timestamp is in milliseconds (> year 2001 in ms)
                        sent_time_seconds = sent_time / 1000
                    else:
                        sent_time_seconds = sent_time
                    
                    current_time = now
                    latency = max(0, (current_time - sent_time_seconds) * 1000)  # Convert to ms
                    self.connections[ws]['latency'] = latency
                    
                    if VERBOSE_LEVEL > 1:
                        print(f"SH: Ping latency: {latency:.2f}ms")
                except (ValueError, TypeError):
                    if VERBOSE_LEVEL > 0:
                        print(f"SH: Invalid timestamp in pong: {timestamp}")
                    pass  # Invalid timestamp, keep previous latency
            
    def get_connection_info(self, ws):
        if ws in self.connections:
            return {
                'latency': self.connections[ws]['latency'],
                'status': self.connections[ws]['status'],
                'last_ping': self.connections[ws]['last_ping'],
                'last_pong': self.connections[ws]['last_pong']
            }
        return None


class PhysicsSimulationManager:
    """Manages physics simulations and their data streams"""
    
    def __init__(self):
        self.simulations = {}  # simulation_id -> simulation_data
        self.active_solvers = {}  # simulation_id -> solver_status
        
    def register_simulation(self, simulation_id, config):
        """Register a new physics simulation"""
        self.simulations[simulation_id] = {
            'id': simulation_id,
            'config': config,
            'status': 'initializing',
            'streams': {},
            'created_at': time.time(),
            'last_update': time.time()
        }
        return self.simulations[simulation_id]
    
    def update_simulation_status(self, simulation_id, status):
        """Update the status of a simulation"""
        if simulation_id in self.simulations:
            self.simulations[simulation_id]['status'] = status
            self.simulations[simulation_id]['last_update'] = time.time()
            return True
        return False
    
    def update_simulation_data(self, simulation_id, stream_id, data):
        """Update data for a specific stream in a simulation"""
        if simulation_id in self.simulations:
            if stream_id not in self.simulations[simulation_id]['streams']:
                self.simulations[simulation_id]['streams'][stream_id] = {}
            
            self.simulations[simulation_id]['streams'][stream_id].update(data)
            self.simulations[simulation_id]['last_update'] = time.time()
            return True
        return False
    
    def get_simulation(self, simulation_id):
        """Get simulation data by ID"""
        return self.simulations.get(simulation_id)
    
    def get_all_simulations(self):
        """Get all active simulations"""
        return self.simulations
    
    def remove_simulation(self, simulation_id):
        """Remove a simulation"""
        if simulation_id in self.simulations:
            del self.simulations[simulation_id]
            return True
        return False


class UnifiedStreamHandler:
    """Unified stream handler with tool calling, physics simulation, and Ally integration"""
    
    def __init__(self, port: int = 3000):
        """Initialize the unified stream handler"""
        self.port = port
        self.app = None
        self.running = False
        self.connection_manager = ConnectionManager()
        self.physics_manager = PhysicsSimulationManager()
        
    def start_sync(self):
        """Start the stream handler (synchronous version for socketify compatibility)"""
        self.running = True
        logger.info(f"Unified Stream Handler v4.0 initialized on port {self.port}")
    
    def stop_sync(self):
        """Stop the stream handler (synchronous version)"""
        self.running = False
        logger.info("Unified Stream Handler v4.0 stopped")
    
    def ws_open(self, ws):
        """Handle new WebSocket connection"""
        if VERBOSE_LEVEL > 0:
            logger.info("New WebSocket connection established")
        
        connected_clients.add(ws)
        self.connection_manager.add_connection(ws)
        
        # Subscribe to all channels
        ws.subscribe("broadcast")
        ws.subscribe("physics")  # Physics simulation channel
        ws.subscribe("tools")    # Tool execution channel
        
        # Send welcome message with comprehensive system info
        welcome_message = {
            "type": "system_info",
            "message": "Connected to Stream Handler v4.0",
            "version": "4.0",
            "features": {
                "tool_execution": True,
                "physics_simulation": True,
                "ally_integration": True,
                "chyappy_protocol": "3.0"
            },
            "supported_message_types": message_registry.list_types(),
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
    
    def ws_close(self, ws, code, message):
        """Handle WebSocket connection close"""
        if VERBOSE_LEVEL > 0:
            logger.info(f"WebSocket connection closed with code {code}")
        
        connected_clients.discard(ws)
        self.connection_manager.remove_connection(ws)
    
    def ws_message(self, ws, message, opcode):
        """Handle incoming WebSocket message"""
        if VERBOSE_LEVEL > 1:
            logger.debug(f"Received message: {message}")
        
        # Always print incoming messages for debugging
        print(f"\n=== STREAM HANDLER v4.0 DEBUG ===")
        print(f"[RECEIVED] Raw message: {message}")
        print(f"[RECEIVED] Message length: {len(message)} characters")
        
        # Create async task to handle the message
        asyncio.create_task(self.handle_message_async(ws, message, opcode))
    
    async def handle_message_async(self, ws, message_str, opcode):
        """Handle message asynchronously with unified routing"""
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
            
            print(f"[PARSED] Message type: {message_type}")
            logger.info(f"Processing message type: {message_type}")
            
            # Route messages based on type
            if message_type in ['tool_call', 'tool_result']:
                # Handle tool execution messages
                await self.handle_tool_messages(ws, message, opcode)
                
            elif message_type == 'physics_simulation':
                # Handle physics simulation messages
                await self.handle_physics_messages(ws, message, opcode)
                
            elif message_type in ['ping', 'pong']:
                # Handle ping/pong messages
                await self.handle_ping_pong_messages(ws, message, opcode)
                
            elif message_type in ['ally_intent', 'ally_memory', 'ally_query', 'ally_status']:
                # Handle Ally cognitive messages
                await self.handle_ally_messages(ws, message, opcode)
                
            elif message_type == 'query':
                # Handle legacy and system queries
                await self.handle_query_messages(ws, message, opcode)
                
            elif message_type == 'negotiation':
                # Handle stream negotiation messages
                await self.handle_negotiation_messages(ws, message, opcode)
                
            elif message_type == 'trading_stream':
                # Handle trading stream messages
                await self.handle_trading_messages(ws, message, opcode)
                
            else:
                # Handle unknown or legacy message types
                await self.handle_unknown_messages(ws, message, message_str, opcode)
                
        except MessageValidationError as e:
            logger.error(f"Message validation error: {e}")
            await self.send_error_response(ws, "VALIDATION_ERROR", str(e))
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await self.send_error_response(ws, "PROCESSING_ERROR", "Internal error processing message")
        
        finally:
            print(f"=== END STREAM HANDLER v4.0 DEBUG ===\n")
    
    async def handle_tool_messages(self, ws, message, opcode):
        """Handle tool execution messages"""
        print(f"[TOOL] Processing tool message: {message.get('type')}")
        
        # Route tool messages to tool handlers
        success = await route_tool_message(
            message, 
            lambda msg: self.broadcast_to_channel("tools", msg, opcode)
        )
        
        if not success:
            await self.send_error_response(
                ws, "TOOL_HANDLER_ERROR", 
                f"Failed to handle {message.get('type')} message"
            )
        else:
            print(f"[TOOL] Successfully processed {message.get('type')} message")
    
    async def handle_physics_messages(self, ws, message, opcode):
        """Handle physics simulation messages"""
        action = message.get('action')
        simulation_id = message.get('simulation_id')
        
        print(f"[PHYSICS] Processing physics message: action={action}, simulation_id={simulation_id}")
        
        if action == 'register':
            # Register a new physics simulation
            config = message.get('config', {})
            simulation = self.physics_manager.register_simulation(simulation_id, config)
            print(f"[PHYSICS] Registered simulation: {simulation_id} with config: {config}")
            
            # Send confirmation back to the simulation
            response = {
                'type': 'physics_simulation',
                'action': 'registered',
                'simulation_id': simulation_id,
                'status': 'success',
                'msg-sent-timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            ws.send(json.dumps(response), OpCode.TEXT)
            
            # Broadcast to physics channel
            unified_message = UnifiedStreamFormat.create_physics_message(
                simulation_id, {}, command='registered')
            self.broadcast_to_channel("physics", json.dumps(unified_message), OpCode.TEXT)
            
        elif action == 'register_stream':
            # Register a new stream for physics simulation
            stream_id = message.get('stream_id')
            stream_data = message.get('stream_data', {})
            
            if stream_id and stream_data:
                # Update physics manager
                self.physics_manager.update_simulation_data(simulation_id, stream_id, stream_data)
                
                # Add to active_streams for AriesUI
                stream_key = f"{simulation_id}_{stream_id}"
                active_streams[stream_key] = {
                    "stream_id": stream_key,
                    "name": f"StarSim {stream_data.get('name', stream_id)}",
                    "datatype": stream_data.get('datatype', 'float'),
                    "unit": stream_data.get('unit', ''),
                    "value": stream_data.get('value', 0.0),
                    "status": stream_data.get('status', 'active'),
                    "timestamp": stream_data.get('timestamp', datetime.now().isoformat()),
                    "simulation_id": simulation_id
                }
                print(f"[PHYSICS] Added to active_streams: {stream_key}")
                
                # Broadcast to main channel for AriesUI
                unified_message = UnifiedStreamFormat.create_negotiation_message(active_streams)
                self.broadcast_to_channel("broadcast", json.dumps(unified_message), OpCode.TEXT)
                
                # Send confirmation back to StarSim
                response = {
                    'type': 'physics_simulation',
                    'action': 'stream_registered',
                    'simulation_id': simulation_id,
                    'stream_id': stream_id,
                    'status': 'success',
                    'msg-sent-timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                ws.send(json.dumps(response), OpCode.TEXT)
                
        elif action == 'update':
            # Update simulation data
            stream_id = message.get('stream_id')
            stream_data = message.get('data', {})
            
            if stream_id and stream_data:
                # Update physics manager
                self.physics_manager.update_simulation_data(simulation_id, stream_id, stream_data)
                
                # Update active_streams for AriesUI
                stream_key = f"{simulation_id}_{stream_id}"
                if stream_key in active_streams:
                    active_streams[stream_key].update({
                        "value": stream_data.get('value', active_streams[stream_key].get('value', 0.0)),
                        "timestamp": stream_data.get('timestamp', datetime.now().isoformat())
                    })
                    if 'vector_value' in stream_data:
                        active_streams[stream_key]['vector_value'] = stream_data['vector_value']
                else:
                    # Create new stream entry if it doesn't exist
                    active_streams[stream_key] = {
                        "stream_id": stream_key,
                        "name": f"StarSim {stream_id}",
                        "datatype": "float",
                        "unit": "",
                        "value": stream_data.get('value', 0.0),
                        "status": "active",
                        "timestamp": stream_data.get('timestamp', datetime.now().isoformat()),
                        "simulation_id": simulation_id
                    }
                    if 'vector_value' in stream_data:
                        active_streams[stream_key]['vector_value'] = stream_data['vector_value']
                
                print(f"[PHYSICS] Updated stream: {stream_key} - value={stream_data.get('value', 'N/A')}")
                
                # Broadcast update to physics channel
                self.broadcast_to_channel("physics", json.dumps({
                    'type': 'physics_simulation',
                    'action': 'updated',
                    'simulation_id': simulation_id,
                    'stream_id': stream_id,
                    'data': stream_data,
                    'msg-sent-timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }), OpCode.TEXT)
                
                # Also broadcast to main channel for AriesUI
                unified_message = UnifiedStreamFormat.create_negotiation_message(active_streams)
                self.broadcast_to_channel("broadcast", json.dumps(unified_message), OpCode.TEXT)
        
        # Handle other physics actions (status, control, remove)
        elif action in ['status', 'control', 'remove']:
            # Broadcast to physics channel for other components to handle
            self.broadcast_to_channel("physics", json.dumps(message), opcode)
    
    async def handle_ping_pong_messages(self, ws, message, opcode):
        """Handle ping/pong messages for connection monitoring"""
        msg_type = message.get('type')
        
        if msg_type == 'ping':
            timestamp = message.get('timestamp')
            target = message.get('target', 'sh')  # Default to 'sh' if not specified
            
            # Only respond if this ping is for us
            if target == 'sh':
                self.connection_manager.update_ping(ws, timestamp)
                ws.send(json.dumps({
                    'type': 'pong',
                    'timestamp': timestamp,  # Echo back the original timestamp
                    'target': target,
                    'server_time': time.time(),
                    'status': 'active',
                    'msg-sent-timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }), OpCode.TEXT)
            else:
                # Forward ping to intended recipient(s)
                self.broadcast_to_channel("broadcast", json.dumps(message), opcode)
        
        elif msg_type == 'pong':
            timestamp = message.get('timestamp')
            target = message.get('target', 'sh')
            if target == 'sh':
                if timestamp:
                    self.connection_manager.update_pong(ws, float(timestamp))
            else:
                # Forward pong responses not meant for SH to other clients
                self.broadcast_to_channel("broadcast", json.dumps(message), opcode)
    
    async def handle_ally_messages(self, ws, message, opcode):
        """Handle Ally cognitive messages"""
        print(f"[ALLY] Processing ally message: {message.get('type')}")
        
        # Broadcast ally messages to all clients
        self.broadcast_to_channel("broadcast", json.dumps(message), opcode)
        logger.info(f"Broadcasted {message.get('type')} message")
    
    async def handle_query_messages(self, ws, message, opcode):
        """Handle query messages"""
        query_type = message.get('query_type')
        
        if query_type == 'active_streams':
            response = {
                'type': 'active_streams',
                'data': active_streams,
                'timestamp': asyncio.get_event_loop().time()
            }
            ws.send(json.dumps(response), OpCode.TEXT)
            
        elif query_type == 'connection_info':
            info = self.connection_manager.get_connection_info(ws)
            if info:
                ws.send(json.dumps({
                    'type': 'connection_info',
                    'data': info,
                    'status': 'active',
                    'msg-sent-timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }))
                
        elif query_type == 'physics_simulations':
            response = {
                'type': 'physics_simulations',
                'data': self.physics_manager.get_all_simulations(),
                'msg-sent-timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            ws.send(json.dumps(response), OpCode.TEXT)
            
        elif query_type == 'physics_simulation':
            simulation_id = message.get('simulation_id')
            if simulation_id:
                simulation = self.physics_manager.get_simulation(simulation_id)
                if simulation:
                    response = {
                        'type': 'physics_simulation',
                        'data': simulation,
                        'msg-sent-timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    ws.send(json.dumps(response), OpCode.TEXT)
                else:
                    await self.send_error_response(ws, "SIMULATION_NOT_FOUND", f"Simulation {simulation_id} not found")
        else:
            # Broadcast unknown queries to other components
            self.broadcast_to_channel("broadcast", json.dumps(message), opcode)
    
    async def handle_negotiation_messages(self, ws, message, opcode):
        """Handle stream negotiation messages"""
        incoming_streams = message.get("data", {})
        
        # Convert to unified format if needed
        for stream_id, stream_data in incoming_streams.items():
            if isinstance(stream_data, dict):
                # Update active streams with unified format
                active_streams[stream_id] = stream_data
        
        # Broadcast unified message
        unified_message = UnifiedStreamFormat.create_negotiation_message(active_streams)
        self.broadcast_to_channel("broadcast", json.dumps(unified_message), opcode)
        logger.info("Processed negotiation message")
    
    async def handle_trading_messages(self, ws, message, opcode):
        """Handle trading stream messages"""
        symbol = message.get('symbol')
        stream_data = message.get('streams', {})
        market_data = message.get('market_data', {})
        
        # Create unified trading message
        unified_message = UnifiedStreamFormat.create_trading_message(
            symbol, stream_data, market_data)
        self.broadcast_to_channel("trading", json.dumps(unified_message), opcode)
    
    async def handle_unknown_messages(self, ws, message, message_str, opcode):
        """Handle unknown or legacy message types"""
        message_type = message.get('type')
        logger.warning(f"Unknown message type: {message_type}")
        
        # Check if it's a deprecated type
        if message_registry.is_deprecated(message_type):
            replacement = message_registry.get_replacement_type(message_type)
            warning_msg = f"Message type '{message_type}' is deprecated"
            if replacement:
                warning_msg += f", use '{replacement}' instead"
            
            await self.send_warning_response(ws, "DEPRECATED_MESSAGE_TYPE", warning_msg)
        
        # Broadcast anyway for backward compatibility
        self.broadcast_to_channel("broadcast", message_str, opcode)
    
    def broadcast_to_channel(self, channel: str, message_str: str, opcode):
        """Broadcast message to a specific channel"""
        try:
            if self.app:
                self.app.publish(channel, message_str, opcode)
                if VERBOSE_LEVEL > 1:
                    logger.debug(f"Message broadcasted to {channel} channel")
        except Exception as e:
            logger.error(f"Error broadcasting to {channel}: {e}")
    
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
connection_manager = ConnectionManager()
physics_manager = PhysicsSimulationManager()

def ws_open(ws):
    """Legacy WebSocket open handler"""
    logger.info("A WebSocket connected!")
    connected_clients.add(ws)
    connection_manager.add_connection(ws)
    ws.subscribe("broadcast")
    ws.subscribe("physics")
    ws.subscribe("tools")

def ws_message(ws, message, opcode):
    """Legacy WebSocket message handler"""
    logger.debug(f"Received message: {message}")
    
    # Create handler instance and process message
    handler = UnifiedStreamHandler()
    handler.connection_manager = connection_manager
    handler.physics_manager = physics_manager
    asyncio.create_task(handler.handle_message_async(ws, message, opcode))

def ws_close(ws, code, message):
    """Legacy WebSocket close handler"""
    logger.info(f"WebSocket closed with code {code}")
    connected_clients.discard(ws)
    connection_manager.remove_connection(ws)


# Main execution
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Unified Stream Handler v4.0")
    parser.add_argument("--port", type=int, default=3000, help="Port to listen on")
    parser.add_argument("--legacy", action="store_true", help="Run in legacy compatibility mode")
    parser.add_argument("--verbose", type=int, default=1, help="Verbose level (0-2)")
    args = parser.parse_args()
    
    VERBOSE_LEVEL = args.verbose
    
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
        app.any("/", lambda res, req: res.end("Stream Handler v4.0 (Legacy Mode)"))
        app.any("/status", lambda res, req: res.end(json.dumps({
            "status": "active",
            "version": "4.0-legacy",
            "connections": len(connected_clients),
            "physics_simulations": len(physics_manager.simulations),
            "tool_support": True,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })))
        app.listen(args.port, lambda config: logger.info(f"Listening on http://localhost:{args.port}"))
        app.run()
    else:
        # Enhanced mode - use new unified handler class
        logger.info("Running in unified mode with tool calling, physics, and Ally support")
        
        # Create and initialize the handler
        handler = UnifiedStreamHandler(args.port)
        
        # Initialize async components
        async def init_async_components():
            global tool_handlers_started
            if not tool_handlers_started:
                await start_tool_handlers()
                tool_handlers_started = True
                logger.info("Tool message handlers started")
        
        # Run async initialization
        asyncio.run(init_async_components())
        
        # Set up the app with socketify's event loop
        app = App()
        app.ws(
            "/*",
            {
                "compression": CompressOptions.SHARED_COMPRESSOR,
                "max_payload_length": 16 * 1024 * 1024,
                "idle_timeout": 60,
                "open": handler.ws_open,
                "message": handler.ws_message,
                "close": handler.ws_close,
            }
        )
        
        # HTTP routes
        app.any("/", lambda res, req: res.end("Stream Handler v4.0 - Tool Calling + Physics + Ally"))
        app.any("/status", lambda res, req: res.end(json.dumps({
            "status": "active",
            "version": "4.0",
            "connections": len(handler.connection_manager.connections),
            "physics_simulations": len(handler.physics_manager.simulations),
            "tool_support": True,
            "supported_message_types": message_registry.list_types(),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })))
        
        # Store app reference in handler for broadcasting
        handler.app = app
        
        logger.info(f"Starting Unified Stream Handler v4.0 on port {args.port}")
        app.listen(args.port, lambda config: logger.info(f"Listening on http://localhost:{args.port}"))
        
        # Let socketify control the event loop
        try:
            app.run()
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        finally:
            # Cleanup async components
            async def cleanup():
                global tool_handlers_started
                if tool_handlers_started:
                    await stop_tool_handlers()
                    tool_handlers_started = False
                    logger.info("Tool message handlers stopped")
            
            asyncio.run(cleanup())
            logger.info("Unified Stream Handler v4.0 stopped")