# sh/sh.py
from socketify import App, OpCode, CompressOptions
import json
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import socket
import sys

active_streams = []
IDLE_TIMEOUT = 60  # Default WebSocket idle timeout
DEBUG_REFRESH = 1000  # Default debug refresh rate in ms
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
        for item in tree.get_children():
            tree.delete(item)
        for module_id, module_data in active_streams.items():
            module_node = tree.insert("", "end", values=(module_id, module_data["name"], module_data["status"], module_data["module-update-timestamp"], "", "", "", ""))
            for stream_id, stream in module_data["streams"].items():
                tree.insert(module_node, "end", values=("", "", "", "", stream_id, stream["name"], str(stream["value"]), stream["stream-update-timestamp"]))
        debug_root.after(DEBUG_REFRESH, update_table)

    update_table()
    debug_root.mainloop()

def create_config_window():
    global IDLE_TIMEOUT, DEBUG_REFRESH, VERBOSE_LEVEL
    config_root = tk.Tk()
    config_root.title("Stream Handler Configuration")
    config_root.geometry("400x300")

    tk.Label(config_root, text="WebSocket Idle Timeout (seconds):").pack(pady=5)
    timeout_entry = tk.Entry(config_root)
    timeout_entry.insert(0, str(IDLE_TIMEOUT))
    timeout_entry.pack()

    tk.Label(config_root, text="Debug Refresh Rate (ms):").pack(pady=5)
    refresh_entry = tk.Entry(config_root)
    refresh_entry.insert(0, str(DEBUG_REFRESH))
    refresh_entry.pack()

    tk.Label(config_root, text="Verbose Level (0-2):").pack(pady=5)
    verbose_entry = tk.Entry(config_root)
    verbose_entry.insert(0, str(VERBOSE_LEVEL))
    verbose_entry.pack()

    def save_config():
        global IDLE_TIMEOUT, DEBUG_REFRESH, VERBOSE_LEVEL
        try:
            timeout = int(timeout_entry.get())
            refresh = int(refresh_entry.get())
            verbose = int(verbose_entry.get())
            if timeout <= 0 or refresh <= 0:
                raise ValueError("Timeout and refresh must be positive")
            if verbose < 0 or verbose > 2:
                raise ValueError("Verbose level must be 0-2")
            IDLE_TIMEOUT = timeout
            DEBUG_REFRESH = refresh
            VERBOSE_LEVEL = verbose
            messagebox.showinfo("Success", "Configuration updated (restart required for WebSocket timeout)")
            config_root.destroy()
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    tk.Button(config_root, text="Save", command=save_config).pack(pady=20)
    config_root.mainloop()

def start_debug_window():
    debug_thread = threading.Thread(target=create_debug_window, daemon=True)
    debug_thread.start()

def start_config_window():
    config_thread = threading.Thread(target=create_config_window, daemon=True)
    config_thread.start()

def debug_socket_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', 5001))
    server.listen(1)
    if VERBOSE_LEVEL > 0:
        print("SH debug socket server listening on localhost:5001")
    while True:
        client, addr = server.accept()
        data = client.recv(1024).decode()
        if data == "debug":
            start_debug_window()
        elif data == "config":
            start_config_window()
        client.close()

debug_thread = threading.Thread(target=debug_socket_server, daemon=True)
debug_thread.start()

app = App()
app.ws(
    "/*",
    {
        "compression": CompressOptions.SHARED_COMPRESSOR,
        "max_payload_length": 16 * 1024 * 1024,
        "idle_timeout": IDLE_TIMEOUT,
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