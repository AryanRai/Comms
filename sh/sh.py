# sh/sh.py
from socketify import App, OpCode, CompressOptions
import json
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import socket
import sys
import time
from datetime import datetime

active_streams = []
IDLE_TIMEOUT = 0.1  # Set WebSocket idle timeout to 100ms
DEBUG_REFRESH = 100  # Default debug refresh rate in ms
VERBOSE_LEVEL = 1  # Default verbose level (Debuglvl)

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
                self.connections[ws]['latency'] = (now - timestamp) * 1000  # Convert to ms
            
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

def ws_open(ws):
    if VERBOSE_LEVEL > 0:
        print("A WebSocket connected!")
    ws.subscribe("broadcast")
    connection_manager.add_connection(ws)
    
    # Send initial ping
    ws.send(json.dumps({
        'type': 'ping',
        'timestamp': time.time(),
        'status': 'active',
        'msg-sent-timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }), OpCode.TEXT)

def ws_message(ws, message, opcode):
    global active_streams
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
                    'timestamp': timestamp,
                    'target': target,
                    'server_time': time.time(),
                    'status': 'active',
                    'msg-sent-timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }))
                return
            else:
                # Forward ping to intended recipient(s)
                ws.publish("broadcast", message, opcode)
                return
        
        elif msg_type == 'pong':
            timestamp = data.get('timestamp')
            target = data.get('target', 'sh')
            if target == 'sh':
                connection_manager.update_pong(ws, timestamp)
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
                if VERBOSE_LEVEL > 0:
                    print("Sent active streams to client.")
                return

        # Handle other message types
        elif msg_type == 'negotiation':
            active_streams = data["data"]  # Update active streams
            ws.publish("broadcast", message, opcode)  # Forward to all clients
        elif msg_type == 'control':
            # Forward control messages to all clients (including Engine)
            ws.publish("broadcast", message, opcode)
            response = {
                'type': 'control_response',
                'module_id': data.get('module_id'),
                'status': 'forwarded',
                'msg-sent-timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            ws.send(json.dumps(response), OpCode.TEXT)
        elif msg_type == 'config_update':
            # Forward config updates to all clients
            ws.publish("broadcast", message, opcode)
            response = {
                'type': 'config_response',
                'module_id': data.get('module_id'),
                'status': 'forwarded',
                'msg-sent-timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            ws.send(json.dumps(response), OpCode.TEXT)
        else:
            # Forward any other messages to all clients
            ws.publish("broadcast", message, opcode)
    except json.JSONDecodeError:
        if VERBOSE_LEVEL > 0:
            print("Error decoding JSON.")

def ws_close(ws):
    connection_manager.remove_connection(ws)
    if VERBOSE_LEVEL > 0:
        print("WebSocket disconnected")

def cleanup():
    if VERBOSE_LEVEL > 0:
        print("Shutting down stream handler...")
    sys.exit(0)

def create_debug_window():
    debug_root = tk.Tk()
    debug_root.title("Stream Handler Debug")
    debug_root.geometry("1000x600")

    # Add control frame
    control_frame = tk.Frame(debug_root)
    control_frame.pack(fill="x", pady=5)
    
    # Add pause button
    paused = False
    def toggle_pause():
        nonlocal paused
        paused = not paused
        pause_button.config(text="Resume" if paused else "Pause")
        
    pause_button = tk.Button(control_frame, text="Pause", command=toggle_pause)
    pause_button.pack(side="left", padx=5)
    
    # Add refresh rate control
    tk.Label(control_frame, text="Display Refresh Rate (ms):").pack(side="left", padx=5)
    refresh_entry = tk.Entry(control_frame, width=10)
    refresh_entry.insert(0, str(DEBUG_REFRESH))
    refresh_entry.pack(side="left", padx=5)
    
    def update_refresh():
        global DEBUG_REFRESH
        try:
            new_rate = int(refresh_entry.get())
            if new_rate > 0:
                DEBUG_REFRESH = new_rate
                messagebox.showinfo("Success", f"Refresh rate updated to {new_rate}ms")
            else:
                messagebox.showerror("Error", "Refresh rate must be positive")
        except ValueError:
            messagebox.showerror("Error", "Invalid refresh rate")
            
    tk.Button(control_frame, text="Update Rate", command=update_refresh).pack(side="left", padx=5)

    # Create tree view for streams
    tree = ttk.Treeview(debug_root, columns=("ModuleID", "Name", "Status", "Timestamp", "StreamID", "StreamName", "Value", "StreamTimestamp"), show="headings")
    tree.heading("ModuleID", text="Module ID")
    tree.heading("Name", text="Module Name")
    tree.heading("Status", text="Status")
    tree.heading("Timestamp", text="Timestamp")
    tree.heading("StreamID", text="Stream ID")
    tree.heading("StreamName", text="Stream Name")
    tree.heading("Value", text="Value")
    tree.heading("StreamTimestamp", text="Stream Timestamp")
    tree.column("ModuleID", width=100)
    tree.column("Name", width=150)
    tree.column("Status", width=80)
    tree.column("Timestamp", width=150)
    tree.column("StreamID", width=100)
    tree.column("StreamName", width=150)
    tree.column("Value", width=80)
    tree.column("StreamTimestamp", width=150)
    tree.pack(fill="both", expand=True)

    def update_table():
        if not paused:
            for item in tree.get_children():
                tree.delete(item)
            for module_id, module_data in active_streams.items():
                module_node = tree.insert("", "end", values=(module_id, module_data["name"], module_data["status"], module_data["module-update-timestamp"], "", "", "", ""))
                tree.item(module_node, open=True)  # Expand module nodes by default
                for stream_id, stream in module_data["streams"].items():
                    tree.insert(module_node, "end", values=("", "", "", "", stream_id, stream["name"], str(stream["value"]), stream["stream-update-timestamp"]))
        debug_root.after(DEBUG_REFRESH, update_table)

    update_table()
    debug_root.mainloop()

def start_debug_window():
    debug_thread = threading.Thread(target=create_debug_window, daemon=True)
    debug_thread.start()

def debug_socket_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server.bind(('localhost', 5001))
        server.listen(1)
        if VERBOSE_LEVEL > 0:
            print("SH debug socket server listening on localhost:5001")
        while True:
            try:
                client, addr = server.accept()
                try:
                    data = client.recv(1024).decode()
                    if data == "debug":
                        start_debug_window()
                finally:
                    client.close()
            except Exception as e:
                if VERBOSE_LEVEL > 0:
                    print(f"Error handling client connection: {e}")
    except Exception as e:
        if VERBOSE_LEVEL > 0:
            print(f"Error in debug socket server: {e}")
    finally:
        server.close()

# Start debug socket server in a separate thread
debug_thread = threading.Thread(target=debug_socket_server, daemon=True)
debug_thread.start()

# Create and configure the WebSocket app
app = App()
app.ws(
    "/*",
    {
        "compression": CompressOptions.SHARED_COMPRESSOR,
        "max_payload_length": 16 * 1024 * 1024,
        "idle_timeout": 960,  # Set WebSocket idle timeout
        "open": ws_open,
        "message": ws_message,
        "close": ws_close,
    }
)

app.any("/", lambda res, req: res.end("Nothing to see here!"))
app.listen(8000, lambda config: print("Listening on http://localhost:8000") if VERBOSE_LEVEL > 0 else None)

try:
    app.run()
except KeyboardInterrupt:
    cleanup()