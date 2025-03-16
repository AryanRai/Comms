# sh/sh.py
from socketify import App, OpCode, CompressOptions
import json
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import socket
import sys

active_streams = []
IDLE_TIMEOUT = 0.1  # Set WebSocket idle timeout to 100ms
DEBUG_REFRESH = 100  # Default debug refresh rate in ms
VERBOSE_LEVEL = 0  # Default verbose level (Debuglvl)

def ws_open(ws):
    if VERBOSE_LEVEL > 0:
        print("A WebSocket connected!")
    ws.subscribe("broadcast")

def ws_message(ws, message, opcode):
    global active_streams
    if VERBOSE_LEVEL > 0:
        print(f"Received message: {message}")
    try:
        data = json.loads(message)
        if data.get('type') == 'query' and data.get('query_type') == 'active_streams':
            response = {
                'type': 'active_streams',
                'data': active_streams
            }
            ws.send(json.dumps(response), OpCode.TEXT)
            if VERBOSE_LEVEL > 0:
                print("Sent active streams to client.")
        elif data.get('type') == 'negotiation':
            active_streams = data["data"]  # Restore original flat structure
            ws.publish("broadcast", message, opcode)
        elif data.get('type') == 'control':
            # Forward control message to all clients (including Engine)
            ws.publish("broadcast", message, opcode)
            response = {
                'type': 'control_response',
                'module_id': data.get('module_id'),
                'status': 'forwarded'
            }
            ws.send(json.dumps(response), OpCode.TEXT)
        elif data.get('type') == 'config_update':
            # Forward config update to all clients (including Engine)
            ws.publish("broadcast", message, opcode)
            response = {
                'type': 'config_response',
                'module_id': data.get('module_id'),
                'status': 'forwarded'
            }
            ws.send(json.dumps(response), OpCode.TEXT)
        else:
            ws.publish("broadcast", message, opcode)
    except json.JSONDecodeError:
        if VERBOSE_LEVEL > 0:
            print("Error decoding JSON.")

def cleanup():
    if VERBOSE_LEVEL > 0:
        print("Shutting down stream handler...")
    sys.exit(0)

def create_debug_window():
    global DEBUG_REFRESH
    debug_root = tk.Tk()
    debug_root.title("Stream Handler Debug")
    debug_root.geometry("800x400")

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
                # Store the open/closed state of each item
                is_open = tree.item(item, "open")
                tree.delete(item)
            for module_id, module_data in active_streams.items():
                module_node = tree.insert("", "end", values=(module_id, module_data["name"], module_data["status"], module_data["module-update-timestamp"], "", "", "", ""))
                # Expand all module nodes by default
                tree.item(module_node, open=True)
                for stream_id, stream in module_data["streams"].items():
                    tree.insert(module_node, "end", values=("", "", "", "", stream_id, stream["name"], str(stream["value"]), stream["stream-update-timestamp"]))
        debug_root.after(DEBUG_REFRESH, update_table)

    update_table()
    debug_root.mainloop()

def create_config_window():
    global IDLE_TIMEOUT, DEBUG_REFRESH, VERBOSE_LEVEL
    config_root = tk.Tk()
    config_root.title("Stream Handler Configuration")
    config_root.geometry("400x400")

    # Add scrollable frame for configurations
    canvas = tk.Canvas(config_root)
    scrollbar = tk.Scrollbar(config_root, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    # WebSocket Configuration
    tk.Label(scrollable_frame, text="WebSocket Configuration", font=("TkDefaultFont", 10, "bold")).pack(pady=10)
    
    tk.Label(scrollable_frame, text="WebSocket Idle Timeout (seconds):").pack(pady=5)
    timeout_entry = tk.Entry(scrollable_frame)
    timeout_entry.insert(0, str(IDLE_TIMEOUT))
    timeout_entry.pack()

    tk.Label(scrollable_frame, text="Max Payload Length (MB):").pack(pady=5)
    payload_entry = tk.Entry(scrollable_frame)
    payload_entry.insert(0, "16")
    payload_entry.pack()

    # Debug Configuration
    tk.Label(scrollable_frame, text="Debug Configuration", font=("TkDefaultFont", 10, "bold")).pack(pady=10)
    
    tk.Label(scrollable_frame, text="Debug Refresh Rate (ms):").pack(pady=5)
    refresh_entry = tk.Entry(scrollable_frame)
    refresh_entry.insert(0, str(DEBUG_REFRESH))
    refresh_entry.pack()

    tk.Label(scrollable_frame, text="Verbose Level (0-2):").pack(pady=5)
    verbose_entry = tk.Entry(scrollable_frame)
    verbose_entry.insert(0, str(VERBOSE_LEVEL))
    verbose_entry.pack()

    def save_config():
        global IDLE_TIMEOUT, DEBUG_REFRESH, VERBOSE_LEVEL
        try:
            timeout = int(timeout_entry.get())
            refresh = int(refresh_entry.get())
            verbose = int(verbose_entry.get())
            payload = int(payload_entry.get())
            
            if timeout <= 0 or refresh <= 0 or payload <= 0:
                raise ValueError("Values must be positive")
            if verbose < 0 or verbose > 2:
                raise ValueError("Verbose level must be 0-2")
                
            IDLE_TIMEOUT = timeout
            DEBUG_REFRESH = refresh
            VERBOSE_LEVEL = verbose
            
            messagebox.showinfo("Success", "Configuration updated\n(restart required for some changes)")
            config_root.destroy()
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    tk.Button(scrollable_frame, text="Save", command=save_config).pack(pady=20)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

def start_debug_window():
    debug_thread = threading.Thread(target=create_debug_window, daemon=True)
    debug_thread.start()

def start_config_window():
    config_thread = threading.Thread(target=create_config_window, daemon=True)
    config_thread.start()

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
                    elif data == "config":
                        start_config_window()
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

debug_thread = threading.Thread(target=debug_socket_server, daemon=True)
debug_thread.start()

app = App()
app.ws(
    "/*",
    {
        "compression": CompressOptions.SHARED_COMPRESSOR,
        "max_payload_length": 16 * 1024 * 1024,
        "idle_timeout": 960,  # Set WebSocket idle timeout to 100ms
        "open": ws_open,
        "message": ws_message,
        "close": lambda ws, code, message: print(f"WebSocket closed with code {code}") if VERBOSE_LEVEL > 0 else None,
    }
)
app.any("/", lambda res, req: res.end("Nothing to see here!"))
app.listen(3000, lambda config: print("Listening on http://localhost:3000") if VERBOSE_LEVEL > 0 else None)
try:
    app.run()
except KeyboardInterrupt:
    cleanup()