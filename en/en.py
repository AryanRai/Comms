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
        if hasattr(self.instance, 'streams'):
            self.streams = self.instance.streams
        if hasattr(self.instance, 'config'):
            self.config = self.instance.config
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
            self.instance.update_multiple_configs(config_updates)
            self.config.update(config_updates)
    
    def control(self, command: str):
        if hasattr(self.instance, 'control_module'):
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
        self.update_rate = 0.01
        
    async def initialize(self):
        await self.module_handler.load_modules()
        
    async def update_values(self):
        while True:
            stream_data = self.module_handler.get_all_stream_data()
            if self.Debuglvl > 1:
                print("Engine: Module Data Update:")
                print(json.dumps(stream_data, indent=2))
            await asyncio.sleep(self.update_rate)

class Negotiator:
    def __init__(self, engine, ws_url='ws://localhost:3000', Debuglvl=0):
        self.engine = engine
        self.ws_url = ws_url
        self.Debuglvl = Debuglvl
        self.ws_session = None
        self.pub_sub_rate = 0.01

    async def ws_pub_sub(self):
        if self.Debuglvl > 0:
            print("Starting pub_sub")
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(self.ws_url) as ws:
                self.ws_session = ws
                while True:
                    if self.Debuglvl > 0:
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
                    response = await ws.receive()
                    if self.Debuglvl > 1:
                        print(f"Negotiator: Received WS: {response.data}")
                    await asyncio.sleep(self.pub_sub_rate)

    async def close(self):
        if self.ws_session:
            await self.ws_session.close()

def create_debug_window(engine):
    debug_root = tk.Tk()
    debug_root.title("Engine Debug")
    debug_root.geometry("1000x600")
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
        module_data = engine.module_handler.get_all_stream_data()
        for module_id, data in module_data.items():
            module_node = tree.insert("", "end", values=(module_id, data["name"], data["status"], data["module-update-timestamp"], "", "", "", ""))
            for stream_id, stream in data["streams"].items():
                tree.insert(module_node, "end", values=("", "", "", "", stream_id, stream["name"], str(stream["value"]), stream["stream-update-timestamp"]))
        debug_root.after(1000, update_table)

    update_table()
    debug_root.mainloop()

def create_config_window(engine, negotiator):
    config_root = tk.Tk()
    config_root.title("Engine Configuration")
    config_root.geometry("400x300")

    tk.Label(config_root, text="Verbose Level (0-2):").pack(pady=5)
    verbose_entry = tk.Entry(config_root)
    verbose_entry.insert(0, str(engine.Debuglvl))
    verbose_entry.pack()

    tk.Label(config_root, text="Update Rate (seconds):").pack(pady=5)
    update_entry = tk.Entry(config_root)
    update_entry.insert(0, str(engine.update_rate))
    update_entry.pack()

    tk.Label(config_root, text="Pub/Sub Rate (seconds):").pack(pady=5)
    pubsub_entry = tk.Entry(config_root)
    pubsub_entry.insert(0, str(negotiator.pub_sub_rate))
    pubsub_entry.pack()

    def save_config():
        try:
            verbose = int(verbose_entry.get())
            update_rate = float(update_entry.get())
            pubsub_rate = float(pubsub_entry.get())
            if verbose < 0 or verbose > 2:
                raise ValueError("Verbose level must be 0-2")
            if update_rate <= 0 or pubsub_rate <= 0:
                raise ValueError("Rates must be positive")
            engine.Debuglvl = verbose
            engine.module_handler.Debuglvl = verbose
            engine.update_rate = update_rate
            negotiator.Debuglvl = verbose
            negotiator.pub_sub_rate = pubsub_rate
            messagebox.showinfo("Success", "Configuration updated")
            config_root.destroy()
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    tk.Button(config_root, text="Save", command=save_config).pack(pady=20)
    config_root.mainloop()

def start_debug_window(engine):
    debug_thread = threading.Thread(target=create_debug_window, args=(engine,), daemon=True)
    debug_thread.start()

def start_config_window(engine, negotiator):
    config_thread = threading.Thread(target=create_config_window, args=(engine, negotiator), daemon=True)
    config_thread.start()

def debug_socket_server(engine, negotiator):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', 5002))
    server.listen(1)
    if engine.Debuglvl > 0:
        print("EN debug socket server listening on localhost:5002")
    while True:
        client, addr = server.accept()
        data = client.recv(1024).decode()
        if data == "debug":
            start_debug_window(engine)
        elif data == "config":
            start_config_window(engine, negotiator)
        client.close()

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