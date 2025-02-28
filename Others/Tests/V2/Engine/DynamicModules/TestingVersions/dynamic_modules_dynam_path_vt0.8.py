import os
import importlib
import sys
import asyncio

class ModuleHandler:
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.modules = {}
        self.module_instances = {}

    def load_modules(self):
        if not os.path.isdir(self.folder_path):
            print(f"Folder '{self.folder_path}' does not exist.")
            return
        
        sys.path.append(self.folder_path)

        for file_name in os.listdir(self.folder_path):
            if file_name.endswith(".py") and file_name != "__init__.py":
                module_name = file_name[:-3]
                try:
                    imported_module = importlib.import_module(module_name)
                    self.modules[module_name] = imported_module
                    print(f"Module '{module_name}' imported successfully.")

                    # Initialize module instance
                    if hasattr(imported_module, module_name):
                        self.module_instances[module_name] = getattr(imported_module, module_name)()
                        print(f"Instance of '{module_name}' created.")
                    else:
                        print(f"Failed to find class '{module_name}' in the module.")

                except Exception as e:
                    print(f"Failed to import module '{module_name}': {e}")

    async def run_module_loops(self, rate=1):
        """Run the update loops for all modules asynchronously."""
        tasks = []
        for module_name, module_instance in self.module_instances.items():
            if hasattr(module_instance, 'update_streams_forever'):
                print(f"Starting update loop for module '{module_name}'")
                tasks.append(asyncio.create_task(module_instance.update_streams_forever(rate)))

        await asyncio.gather(*tasks)

    def get_module_streams(self):
        """Retrieve the streams from each module."""
        streams_data = {}
        for module_name, module_instance in self.module_instances.items():
            if hasattr(module_instance, 'get_streams'):
                streams_data[module_name] = module_instance.get_streams()
        return streams_data

    def set_module_stream(self, module_name, stream_id, value):
        """Set a specific stream value in a module."""
        module_instance = self.module_instances.get(module_name)
        if module_instance and hasattr(module_instance, 'set_stream'):
            module_instance.set_stream(stream_id, value)
        else:
            print(f"Module '{module_name}' or stream '{stream_id}' not found.")

    def control_module(self, module_name, command):
        """Send a control command to a module."""
        module_instance = self.module_instances.get(module_name)
        if module_instance and hasattr(module_instance, 'control_module'):
            module_instance.control_module(command)
        else:
            print(f"Module '{module_name}' does not support control commands.")

    async def test_stream_values(self, rate=2):
        """Test function to print streams periodically."""
        while True:
            streams = self.get_module_streams()
            for module_name, module_streams in streams.items():
                print(f"Streams from module '{module_name}': {module_streams}")
            await asyncio.sleep(rate)

# Example usage
if __name__ == "__main__":
    folder_path = "./DynamicModules"
    handler = ModuleHandler(folder_path)

    handler.load_modules()

    # Start the event loop to run module stream updates
    loop = asyncio.get_event_loop()
    try:
        # Run the module loops and test stream printing concurrently
        loop.run_until_complete(asyncio.gather(
            handler.run_module_loops(rate=1),  # Update streams every 1 second
            handler.test_stream_values(rate=0.001)  # Print stream values every 2 seconds
        ))

    except KeyboardInterrupt:
        pass
    finally:
        loop.close()