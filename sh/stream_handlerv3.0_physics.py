from socketify import App, OpCode, CompressOptions
import json
import time
from datetime import datetime
import asyncio
import threading
import sys
import os

# Configuration
IDLE_TIMEOUT = 0.1  # Set WebSocket idle timeout to 100ms
DEBUG_REFRESH = 100  # Default debug refresh rate in ms
VERBOSE_LEVEL = 1  # Default verbose level (Debuglvl)

# Active data streams
active_streams = []
physics_streams = []  # New: Dedicated physics simulation streams

# Print banner
print("=" * 80)
print("Stream Handler v3.0 with Physics Support")
print("Integrated with StarSim ParsecCore")
print("=" * 80)

class ConnectionManager:
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

connection_manager = ConnectionManager()

# New: Physics simulation manager
class PhysicsSimulationManager:
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

physics_manager = PhysicsSimulationManager()

def ws_open(ws):
    if VERBOSE_LEVEL > 0:
        print("A WebSocket connected!")
    ws.subscribe("broadcast")
    ws.subscribe("physics")  # New: Subscribe to physics-specific channel
    connection_manager.add_connection(ws)
    
    # Send initial ping
    ws.send(json.dumps({
        'type': 'ping',
        'timestamp': time.time(),
        'status': 'active',
        'msg-sent-timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }), OpCode.TEXT)

def ws_message(ws, message, opcode):
    global active_streams, physics_streams
    if VERBOSE_LEVEL > 0:
        print(f"Received message: {message}")
    try:
        data = json.loads(message)
        msg_type = data.get('type')

        # Handle ping/pong messages
        if msg_type == 'ping':
            timestamp = data.get('timestamp')
            target = data.get('target', 'sh')  # Default to 'sh' if not specified
            
            # Only respond if this ping is for us
            if target == 'sh':
                connection_manager.update_ping(ws, timestamp)
                ws.send(json.dumps({
                    'type': 'pong',
                    'timestamp': timestamp,  # Echo back the original timestamp
                    'target': target,
                    'server_time': time.time(),
                    'status': 'active',
                    'msg-sent-timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }), OpCode.TEXT)
                return
            else:
                # Forward ping to intended recipient(s)
                ws.publish("broadcast", message, opcode)
                return
        
        elif msg_type == 'pong':
            timestamp = data.get('timestamp')
            target = data.get('target', 'sh')
            if target == 'sh':
                if timestamp:
                    connection_manager.update_pong(ws, float(timestamp))
                return
            else:
                # Forward pong responses not meant for SH to other clients (e.g., UI)
                ws.publish("broadcast", message, opcode)
                return

        # Handle connection info queries
        elif msg_type == 'query':
            if data.get('query_type') == 'connection_info':
                info = connection_manager.get_connection_info(ws)
                if info:
                    ws.send(json.dumps({
                        'type': 'connection_info',
                        'data': info,
                        'status': 'active',
                        'msg-sent-timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }))
                    return
            elif data.get('query_type') == 'active_streams':
                response = {
                    'type': 'active_streams',
                    'data': active_streams,
                    'msg-sent-timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                ws.send(json.dumps(response), OpCode.TEXT)
                return
            # New: Query for physics simulations
            elif data.get('query_type') == 'physics_simulations':
                response = {
                    'type': 'physics_simulations',
                    'data': physics_manager.get_all_simulations(),
                    'msg-sent-timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                ws.send(json.dumps(response), OpCode.TEXT)
                return
            # New: Query for specific physics simulation
            elif data.get('query_type') == 'physics_simulation':
                simulation_id = data.get('simulation_id')
                if simulation_id:
                    simulation = physics_manager.get_simulation(simulation_id)
                    if simulation:
                        response = {
                            'type': 'physics_simulation',
                            'data': simulation,
                            'msg-sent-timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        ws.send(json.dumps(response), OpCode.TEXT)
                        return
                    else:
                        response = {
                            'type': 'error',
                            'error': f"Simulation {simulation_id} not found",
                            'msg-sent-timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        ws.send(json.dumps(response), OpCode.TEXT)
                        return

        # New: Handle physics simulation messages
        elif msg_type == 'physics_simulation':
            action = data.get('action')
            simulation_id = data.get('simulation_id')
            
            if action == 'register':
                # Register a new physics simulation
                config = data.get('config', {})
                simulation = physics_manager.register_simulation(simulation_id, config)
                physics_streams.append(simulation)
                
                # Broadcast to physics channel
                ws.publish("physics", json.dumps({
                    'type': 'physics_simulation',
                    'action': 'registered',
                    'simulation_id': simulation_id,
                    'status': 'initializing',
                    'msg-sent-timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }), OpCode.TEXT)
                return
                
            elif action == 'update':
                # Update simulation data
                stream_id = data.get('stream_id')
                stream_data = data.get('data', {})
                
                if physics_manager.update_simulation_data(simulation_id, stream_id, stream_data):
                    # Broadcast update to physics channel
                    ws.publish("physics", json.dumps({
                        'type': 'physics_simulation',
                        'action': 'updated',
                        'simulation_id': simulation_id,
                        'stream_id': stream_id,
                        'data': stream_data,
                        'msg-sent-timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }), OpCode.TEXT)
                    return
                else:
                    response = {
                        'type': 'error',
                        'error': f"Simulation {simulation_id} not found",
                        'msg-sent-timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    ws.send(json.dumps(response), OpCode.TEXT)
                    return
                    
            elif action == 'status':
                # Update simulation status
                status = data.get('status')
                if physics_manager.update_simulation_status(simulation_id, status):
                    # Broadcast status update to physics channel
                    ws.publish("physics", json.dumps({
                        'type': 'physics_simulation',
                        'action': 'status',
                        'simulation_id': simulation_id,
                        'status': status,
                        'msg-sent-timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }), OpCode.TEXT)
                    return
                else:
                    response = {
                        'type': 'error',
                        'error': f"Simulation {simulation_id} not found",
                        'msg-sent-timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    ws.send(json.dumps(response), OpCode.TEXT)
                    return
                    
            elif action == 'control':
                # Control commands for simulation (start, pause, stop, etc.)
                command = data.get('command')
                params = data.get('params', {})
                
                # Broadcast control command to physics channel
                ws.publish("physics", json.dumps({
                    'type': 'physics_simulation',
                    'action': 'control',
                    'simulation_id': simulation_id,
                    'command': command,
                    'params': params,
                    'msg-sent-timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }), OpCode.TEXT)
                return
                
            elif action == 'remove':
                # Remove a simulation
                if physics_manager.remove_simulation(simulation_id):
                    # Broadcast removal to physics channel
                    ws.publish("physics", json.dumps({
                        'type': 'physics_simulation',
                        'action': 'removed',
                        'simulation_id': simulation_id,
                        'msg-sent-timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }), OpCode.TEXT)
                    return
                else:
                    response = {
                        'type': 'error',
                        'error': f"Simulation {simulation_id} not found",
                        'msg-sent-timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    ws.send(json.dumps(response), OpCode.TEXT)
                    return

        # Handle standard negotiation messages
        elif msg_type == 'negotiation':
            active_streams = data.get("data", [])
            ws.publish("broadcast", message, opcode)
            return

        # Default: broadcast to all clients
        ws.publish("broadcast", message, opcode)
        
    except json.JSONDecodeError:
        print("Error decoding JSON message.")
    except Exception as e:
        print(f"Error processing message: {str(e)}")

def ws_close(ws, code, message):
    print(f"WebSocket closed with code {code}")
    connection_manager.remove_connection(ws)

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
        "close": ws_close,
    }
)

# HTTP routes
app.any("/", lambda res, req: res.end("Stream Handler v3.0 with Physics Support"))
app.any("/status", lambda res, req: res.end(json.dumps({
    "status": "active",
    "connections": len(connection_manager.connections),
    "physics_simulations": len(physics_manager.simulations),
    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
})))

# Start server
if __name__ == "__main__":
    port = 3000
    print(f"Starting Stream Handler v3.0 with Physics Support on port {port}")
    app.listen(port, lambda config: print(f"Listening on http://localhost:{port}"))
    app.run()