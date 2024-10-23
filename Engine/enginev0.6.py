import asyncio
import aiohttp
import json
import os
import importlib
import sys
from datetime import datetime
from typing import Dict, Any, Optional


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
        """Initialize the module and its streams"""
        if hasattr(self.instance, 'streams'):
            self.streams = self.instance.streams
        if hasattr(self.instance, 'config'):
            self.config = self.instance.config
        self.status = "active"
        
    async def update(self):
        """Run the module's update cycle"""
        if hasattr(self.instance, 'update_streams_forever'):
            await self.instance.update_streams_forever()
            self.module_update_timestamp = datetime.now()
            
    def get_stream_data(self) -> dict:
        """Get all stream data from the module"""
        return {
            "module_id": self.module_id,
            "name": self.name,
            "status": self.status,
            "module-update-timestamp": self.module_update_timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "config": self.config,
            "streams": {k: v.to_dict() for k, v in self.streams.items()}
        }
    
    def update_config(self, config_updates: dict):
        """Update module configuration"""
        if hasattr(self.instance, 'update_multiple_configs'):
            self.instance.update_multiple_configs(config_updates)
            self.config.update(config_updates)
    
    def control(self, command: str):
        """Send control command to module"""
        if hasattr(self.instance, 'control_module'):
            self.instance.control_module(command)

class ModuleHandler:
    def __init__(self, folder_path: str = "./DynamicModules", Debuglvl: int = 0):
        self.folder_path = folder_path
        self.Debuglvl = Debuglvl
        self.modules: Dict[str, Module] = {}

    async def load_modules(self):
        """Dynamically load all hardware modules from the 'modules' folder."""
        if not os.path.isdir(self.folder_path):
            print(f"Folder '{self.folder_path}' does not exist.")
            return

        sys.path.append(self.folder_path)

        for file_name in os.listdir(self.folder_path):
            if file_name.endswith(".py") and file_name != "__init__.py":
                module_name = file_name[:-3]
                try:
                    # Import the module
                    imported_module = importlib.import_module(module_name)
                    
                    if self.Debuglvl > 0:
                        print(f"Module '{module_name}' imported successfully.")

                    # Initialize module instance
                    if hasattr(imported_module, module_name):
                        instance = getattr(imported_module, module_name)()
                        
                        # Create Module wrapper
                        module = Module(
                            module_id=module_name,
                            name=module_name.replace('_', ' ').title(),
                            instance=instance
                        )
                        
                        # Initialize the module
                        await module.initialize()
                        
                        # Store the module
                        self.modules[module_name] = module
                        
                        if self.Debuglvl > 0:
                            print(f"Module '{module_name}' initialized and registered.")
                    else:
                        print(f"Failed to find class '{module_name}' in the module.")

                except Exception as e:
                    print(f"Failed to import module '{module_name}': {e}")

    async def run(self):
        """Run all loaded modules' update loops."""
        tasks = []
        for module in self.modules.values():
            tasks.append(asyncio.create_task(module.update()))
        await asyncio.gather(*tasks)

    def get_all_stream_data(self) -> Dict[str, dict]:
        """Get current stream data from all modules."""
        return {module_id: module.get_stream_data() 
                for module_id, module in self.modules.items()}

    def get_module(self, module_id: str) -> Optional[Module]:
        """Get a specific module by ID."""
        return self.modules.get(module_id)

    async def cleanup(self):
        """Cleanup resources."""
        for module in self.modules.values():
            if hasattr(module.instance, 'cleanup'):
                await module.instance.cleanup()

class Engine:
    def __init__(self, Debuglvl=0):
        self.Debuglvl = Debuglvl
        self.module_handler = ModuleHandler(Debuglvl=Debuglvl)
        
    async def initialize(self):
        """Initialize the engine and load modules."""
        await self.module_handler.load_modules()
        
    async def update_values(self, rate):
        """Update values from all dynamic modules."""
        while True:
            stream_data = self.module_handler.get_all_stream_data()
            
            if self.Debuglvl > 1:
                print("Engine: Module Data Update:")
                print(json.dumps(stream_data, indent=2))
                
            await asyncio.sleep(rate)


class Negotiator:
    def __init__(self, engine, ws_url='ws://localhost:3000', Debuglvl=0):
        self.engine = engine
        self.ws_url = ws_url
        self.Debuglvl = Debuglvl
        self.ws_session = None

    async def ws_pub_sub(self, rate):
        if self.Debuglvl > 0:
            print("Starting pub_sub")

        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(self.ws_url) as ws:
                self.ws_session = ws

                while True:
                    if self.Debuglvl > 0:
                        print("Negotiator: Sending WS message")

                    # Get stream data from all modules
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

                    await asyncio.sleep(rate)

    async def close(self):
        if self.ws_session:
            await self.ws_session.close()


async def main():
    engine = Engine(Debuglvl=1)
    await engine.initialize()  # Initialize engine and load modules
    
    negotiator = Negotiator(engine, ws_url='ws://localhost:3000', Debuglvl=1)

    # Run all tasks concurrently
    await asyncio.gather(
        engine.update_values(0.01),
        engine.module_handler.run(),
        negotiator.ws_pub_sub(0.01)
    )


if __name__ == "__main__":
    asyncio.run(main())


























