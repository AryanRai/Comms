#define communication types
from importlib.machinery import SourceFileLoader

class output:
    def __init__(self):
        self.type = "output"
        self.data = []

    def bluetooth(self):
        bluetooth = SourceFileLoader("MAVlink","Modules/RPi_Mavlink/Engine/Mavlink.py").load_module()

class input:
    def __init__(self):
        self.type = "input"
        self.data = []


output = output()
blue = output.bluetooth()