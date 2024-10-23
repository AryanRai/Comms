import os
import importlib
import sys

class ModuleHandler:
    def __init__(self):
        # If running as a compiled executable, set the correct base path
        if getattr(sys, 'frozen', False):  # Check if the program is 'frozen' by PyInstaller
            base_path = sys._MEIPASS       # Get the path to the bundled resources
        else:
            base_path = os.path.abspath(".")  # Otherwise, use the current directory

        # Folder path where the modules are located (relative to the executable)
        self.folder_path = os.path.join(base_path, "DynamicModules")
        self.modules = {}

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
                except Exception as e:
                    print(f"Failed to import module '{module_name}': {e}")
    
    def get_module(self, module_name):
        return self.modules.get(module_name, None)

if __name__ == "__main__":
    handler = ModuleHandler()
    handler.load_modules()

    # Example usage
    my_module = handler.get_module("example_module")
    if my_module:
        print(f"Module '{my_module.__name__}' is loaded.")
