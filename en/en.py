# en/en.py
import asyncio
import aiohttp
import json
import os
import importlib
import sys
from datetime import datetime
from typing import Dict, Any, Optional
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import socket

class Stream:
    def __init__(self, stream_id, name, datatype, unit, status, metadata):
        self.stream_id = stream_id
        self.data = {
            "stream_id": stream_id,
            "name": name,
            "datatype": datatype,
            "unit": unit,
            "status": status,
            "metadata": metadata,
            "value": 0,
            "stream-update-timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "priority": "high"
        }

    def update_value(self, value):
        self.data["value"] = value
        self.data["stream-update-timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self):
        return self.data

class Module:
    def __init__(self, module_id: str, name: str, instance: Any):
        self.module_id = module_id
        self.name = name
        self.instance = instance
        self.streams: Dict[str, Stream] = {}
        self.config: Dict[str, Any] = {}
        self.status = "inactive"
        self.module_update_timestamp = datetime.now()
        
    async def initialize(self):
        """Initialize module attributes safely"""
        # First get config if available
        if hasattr(self.instance, 'config'):
            self.config = self.instance.config
        
        # Then get streams if available
        if hasattr(self.instance, 'streams'):
            self.streams = self.instance.streams
            
        # Mark as active only after successful initialization
        self.status = "active"
        
    async def update(self):
        if hasattr(self.instance, 'update_streams_forever'):
            await self.instance.update_streams_forever()
            self.module_update_timestamp = datetime.now()
            
    def get_stream_data(self) -> dict:
        return {
            "module_id": self.module_id,
            "name": self.name,
            "status": self.status,
            "module-update-timestamp": self.module_update_timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "config": self.config,
            "streams": {k: v.to_dict() for k, v in self.streams.items()}
        }
    
    def update_config(self, config_updates: dict):
        if hasattr(self.instance, 'update_multiple_configs'):
            # Check for stream value updates and log them
            for key, value in config_updates.items():
                if key.endswith('_value'):
                    stream_id = key.replace('_value', '')
                    if stream_id in self.streams:
                        print(f"Engine: Stream update for {self.module_id}.{stream_id}: {value}")
                        if hasattr(self.instance, 'log_stream_update'):
                            self.instance.log_stream_update(stream_id, value)
            
            # Update the configs
            self.instance.update_multiple_configs(config_updates)
            self.config.update(config_updates)
    
    def control(self, command: str):
        if hasattr(self.instance, 'control_module'):
            print(f"Engine: Control command for {self.module_id}: {command}")
            if hasattr(self.instance, 'log_control_command'):
                self.instance.log_control_command(command)
            self.instance.control_module(command)

class ModuleHandler:
    def __init__(self, folder_path: str = "./DynamicModules", Debuglvl: int = 0):
        self.folder_path = folder_path
        self.Debuglvl = Debuglvl
        self.modules: Dict[str, Module] = {}

    async def load_modules(self):
        if not os.path.isdir(self.folder_path):
            if self.Debuglvl > 0:
                print(f"Folder '{self.folder_path}' does not exist.")
            return

        sys.path.append(self.folder_path)

        for file_name in os.listdir(self.folder_path):
            if file_name.endswith(".py") and file_name != "__init__.py":
                module_name = file_name[:-3]
                try:
                    imported_module = importlib.import_module(module_name)
                    if self.Debuglvl > 0:
                        print(f"Module '{module_name}' imported successfully.")
                    if hasattr(imported_module, module_name):
                        instance = getattr(imported_module, module_name)()
                        module = Module(module_id=module_name, name=module_name.replace('_', ' ').title(), instance=instance)
                        await module.initialize()
                        self.modules[module_name] = module
                        if self.Debuglvl > 0:
                            print(f"Module '{module_name}' initialized and registered.")
                    else:
                        if self.Debuglvl > 0:
                            print(f"Failed to find class '{module_name}' in the module.")
                except Exception as e:
                    if self.Debuglvl > 0:
                        print(f"Failed to import module '{module_name}': {e}")

    async def run(self):
        tasks = []
        for module in self.modules.values():
            tasks.append(asyncio.create_task(module.update()))
        await asyncio.gather(*tasks)

    def get_all_stream_data(self) -> Dict[str, dict]:
        return {module_id: module.get_stream_data() for module_id, module in self.modules.items()}

    def get_module(self, module_id: str) -> Optional[Module]:
        return self.modules.get(module_id)

    async def cleanup(self):
        for module in self.modules.values():
            if hasattr(module.instance, 'cleanup'):
                await module.instance.cleanup()

class Engine:
    def __init__(self, Debuglvl=0):
        self.Debuglvl = Debuglvl
        self.module_handler = ModuleHandler(Debuglvl=Debuglvl)
        self.update_rate = 0.1  # 100ms update rate
        
    async def initialize(self):
        await self.module_handler.load_modules()
        
    async def update_values(self):
        while True:
            stream_data = self.module_handler.get_all_stream_data()
            if self.Debuglvl > 1:
                print("Engine: Module Data Update:")
                print(json.dumps(stream_data, indent=2))
            await asyncio.sleep(self.update_rate)  # 100ms sleep

class Negotiator:
    def __init__(self, engine, ws_url='ws://localhost:3000', Debuglvl=0):
        self.engine = engine
        self.ws_url = ws_url
        self.Debuglvl = Debuglvl
        self.ws_session = None
        self.pub_sub_rate = 0.1  # 100ms pub/sub rate

    async def ws_pub_sub(self):
        if self.Debuglvl > 0:
            print("Starting pub_sub")
        async with aiohttp.ClientSession() as session:
            while True:
                try:
                    async with session.ws_connect(self.ws_url) as ws:
                        self.ws_session = ws
                        while True:
                            try:
                                # Send module data
                                if self.Debuglvl > 1:
                                    print("Negotiator: Sending WS message")
                                module_data = self.engine.module_handler.get_all_stream_data()
                                negotiation = {
                                    "type": "negotiation",
                                    "status": "active",
                                    "data": module_data,
                                    "msg-sent-timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                }
                                message = json.dumps(negotiation)
                                await ws.send_str(message)
                                if self.Debuglvl > 1:
                                    print(f"Negotiator: Sent: {message}")
                                
                                # Receive and process messages
                                try:
                                    response = await asyncio.wait_for(ws.receive(), timeout=0.1)  # 100ms timeout
                                    if self.Debuglvl > 1:
                                        print(f"Negotiator: Received WS: {response.data}")
                                    
                                    # Handle incoming messages
                                    if response.type == aiohttp.WSMsgType.TEXT:
                                        data = json.loads(response.data)
                                        if data.get('type') == 'control':
                                            await self.handle_control_message(data)
                                        elif data.get('type') == 'config_update':
                                            await self.handle_config_message(data)
                                except asyncio.TimeoutError:
                                    pass  # No message received within timeout, continue with next update
                                
                                await asyncio.sleep(self.pub_sub_rate)  # 100ms sleep
                            except Exception as e:
                                if self.Debuglvl > 0:
                                    print(f"Error in ws_pub_sub loop: {e}")
                                await asyncio.sleep(0.1)  # 100ms sleep on error
                except Exception as e:
                    if self.Debuglvl > 0:
                        print(f"Error in ws connection: {e}")
                    await asyncio.sleep(0.1)  # 100ms sleep on connection error

    async def handle_control_message(self, data):
        """Handle control messages from UI via stream handler"""
        module_id = data.get('module_id')
        command = data.get('command')
        if module_id and command:
            module = self.engine.module_handler.get_module(module_id)
            if module:
                try:
                    module.control(command)
                    debug_messages = []
                    if hasattr(module.instance, 'get_debug_messages'):
                        debug_messages = module.instance.get_debug_messages()
                    response = {
                        "type": "control_response",
                        "module_id": module_id,
                        "status": "success",
                        "debug_messages": debug_messages,
                        "msg-sent-timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                except Exception as e:
                    response = {
                        "type": "control_response",
                        "module_id": module_id,
                        "status": "error",
                        "error": str(e),
                        "msg-sent-timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                await self.ws_session.send_str(json.dumps(response))

    async def handle_config_message(self, data):
        """Handle config update messages from UI via stream handler"""
        module_id = data.get('module_id')
        config = data.get('config')
        if module_id and config:
            module = self.engine.module_handler.get_module(module_id)
            if module:
                try:
                    module.update_config(config)
                    debug_messages = []
                    if hasattr(module.instance, 'get_debug_messages'):
                        debug_messages = module.instance.get_debug_messages()
                    response = {
                        "type": "config_response",
                        "module_id": module_id,
                        "status": "success",
                        "debug_messages": debug_messages,
                        "msg-sent-timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                except Exception as e:
                    response = {
                        "type": "config_response",
                        "module_id": module_id,
                        "status": "error",
                        "error": str(e),
                        "msg-sent-timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                await self.ws_session.send_str(json.dumps(response))

    async def close(self):
        if self.ws_session:
            await self.ws_session.close()

def create_debug_window(engine):
    debug_root = tk.Tk()
    debug_root.title("Engine Debug")
    debug_root.geometry("1000x600")

    # Add control frame
    control_frame = tk.Frame(debug_root)
    control_frame.pack(fill="x", pady=5)
    
    # Add pause button and refresh rate control
    paused = False
    def toggle_pause():
        nonlocal paused
        paused = not paused
        pause_button.config(text="Resume" if paused else "Pause")
        
    pause_button = tk.Button(control_frame, text="Pause", command=toggle_pause)
    pause_button.pack(side="left", padx=5)
    
    # Add refresh rate control
    tk.Label(control_frame, text="Refresh Rate (ms):").pack(side="left", padx=5)
    refresh_entry = tk.Entry(control_frame, width=10)
    refresh_entry.insert(0, "100")  # Default to 100ms
    refresh_entry.pack(side="left", padx=5)
    
    refresh_rate = 100  # Default refresh rate in ms
    
    def update_refresh():
        nonlocal refresh_rate
        try:
            new_rate = int(refresh_entry.get())
            if new_rate > 0:
                refresh_rate = new_rate
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
            module_data = engine.module_handler.get_all_stream_data()
            for module_id, data in module_data.items():
                module_node = tree.insert("", "end", values=(module_id, data["name"], data["status"], data["module-update-timestamp"], "", "", "", ""))
                # Expand all module nodes by default
                tree.item(module_node, open=True)
                for stream_id, stream in data["streams"].items():
                    tree.insert(module_node, "end", values=("", "", "", "", stream_id, stream["name"], str(stream["value"]), stream["stream-update-timestamp"]))
        debug_root.after(refresh_rate, update_table)  # Use configurable refresh rate

    update_table()
    debug_root.mainloop()

def create_config_window(engine, negotiator):
    config_root = tk.Tk()
    config_root.title("Engine Configuration")
    config_root.geometry("400x500")

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

    # Engine Configuration
    tk.Label(scrollable_frame, text="Engine Configuration", font=("TkDefaultFont", 10, "bold")).pack(pady=10)
    
    tk.Label(scrollable_frame, text="Verbose Level (0-2):").pack(pady=5)
    verbose_entry = tk.Entry(scrollable_frame)
    verbose_entry.insert(0, str(engine.Debuglvl))
    verbose_entry.pack()

    tk.Label(scrollable_frame, text="Update Rate (seconds):").pack(pady=5)
    update_entry = tk.Entry(scrollable_frame)
    update_entry.insert(0, str(engine.update_rate))
    update_entry.pack()

    # Negotiator Configuration
    tk.Label(scrollable_frame, text="Negotiator Configuration", font=("TkDefaultFont", 10, "bold")).pack(pady=10)
    
    tk.Label(scrollable_frame, text="Pub/Sub Rate (seconds):").pack(pady=5)
    pubsub_entry = tk.Entry(scrollable_frame)
    pubsub_entry.insert(0, str(negotiator.pub_sub_rate))
    pubsub_entry.pack()

    tk.Label(scrollable_frame, text="WebSocket URL:").pack(pady=5)
    ws_entry = tk.Entry(scrollable_frame)
    ws_entry.insert(0, negotiator.ws_url)
    ws_entry.pack()

    def save_config():
        try:
            verbose = int(verbose_entry.get())
            update_rate = float(update_entry.get())
            pubsub_rate = float(pubsub_entry.get())
            ws_url = ws_entry.get()

            if verbose < 0 or verbose > 2:
                raise ValueError("Verbose level must be 0-2")
            if update_rate <= 0 or pubsub_rate <= 0:
                raise ValueError("Rates must be positive")
            if not ws_url.startswith(("ws://", "wss://")):
                raise ValueError("WebSocket URL must start with ws:// or wss://")

            engine.Debuglvl = verbose
            engine.module_handler.Debuglvl = verbose
            engine.update_rate = update_rate
            negotiator.Debuglvl = verbose
            negotiator.pub_sub_rate = pubsub_rate
            negotiator.ws_url = ws_url

            messagebox.showinfo("Success", "Configuration updated\n(some changes require restart)")
            config_root.destroy()
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    tk.Button(scrollable_frame, text="Save", command=save_config).pack(pady=20)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    config_root.mainloop()

def start_debug_window(engine):
    debug_thread = threading.Thread(target=create_debug_window, args=(engine,), daemon=True)
    debug_thread.start()

def start_config_window(engine, negotiator):
    config_thread = threading.Thread(target=create_config_window, args=(engine, negotiator), daemon=True)
    config_thread.start()

def debug_socket_server(engine, negotiator):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server.bind(('localhost', 5002))
        server.listen(1)
        if engine.Debuglvl > 0:
            print("EN debug socket server listening on localhost:5002")
        while True:
            client, addr = server.accept()
            try:
                data = client.recv(1024).decode()
                if data == "debug":
                    start_debug_window(engine)
                elif data == "config":
                    start_config_window(engine, negotiator)
                elif data == "get_modules":
                    # Get list of all module IDs
                    module_list = list(engine.module_handler.modules.keys())
                    client.sendall(json.dumps(module_list).encode())
                elif data == "get_config":
                    # Get current configuration values
                    config = {
                        "engine_rate": engine.update_rate,
                        "negotiator_rate": negotiator.pub_sub_rate,
                        "debug_level": engine.Debuglvl,
                        "module_rates": {},
                        "module_configs": {}
                    }
                    # Get module rates and configs
                    for module_id, module in engine.module_handler.modules.items():
                        config["module_rates"][module_id] = module.config.get('update_rate', 0.1)
                        config["module_configs"][module_id] = module.config
                    client.sendall(json.dumps(config).encode())
                elif data.startswith("update_rates:"):
                    try:
                        # Parse the configuration data
                        config_data = json.loads(data.split("update_rates:", 1)[1])
                        
                        # Update Engine rate
                        engine.update_rate = config_data["engine_rate"]
                        
                        # Update Negotiator rate
                        negotiator.pub_sub_rate = config_data["negotiator_rate"]
                        
                        # Update debug level if provided
                        if "debug_level" in config_data:
                            engine.Debuglvl = config_data["debug_level"]
                            engine.module_handler.Debuglvl = config_data["debug_level"]
                            negotiator.Debuglvl = config_data["debug_level"]
                        
                        # Update module rates and configs
                        for module_id, rate in config_data["module_rates"].items():
                            module = engine.module_handler.get_module(module_id)
                            if module:
                                module.config['update_rate'] = rate
                                
                        if "module_configs" in config_data:
                            for module_id, config in config_data["module_configs"].items():
                                module = engine.module_handler.get_module(module_id)
                                if module:
                                    module.update_config(config)
                        
                        client.sendall(b"success")
                    except Exception as e:
                        if engine.Debuglvl > 0:
                            print(f"Error updating rates: {e}")
                        client.sendall(str(e).encode())
            finally:
                client.close()
    except Exception as e:
        if engine.Debuglvl > 0:
            print(f"Error in debug socket server: {e}")
    finally:
        server.close()

async def main():
    engine = Engine(Debuglvl=1)
    await engine.initialize()
    negotiator = Negotiator(engine, ws_url='ws://localhost:3000', Debuglvl=1)
    debug_thread = threading.Thread(target=debug_socket_server, args=(engine, negotiator), daemon=True)
    debug_thread.start()
    await asyncio.gather(
        engine.update_values(),
        engine.module_handler.run(),
        negotiator.ws_pub_sub()
    )

if __name__ == "__main__":
    asyncio.run(main())