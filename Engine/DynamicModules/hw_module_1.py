# hw_module_1.py
#v1.5

import random
import asyncio
from datetime import datetime
from __init__ import Stream

class hw_module_1:
    """Hardware module for temperature and pressure sensors"""
    
    def __init__(self):
        # Module metadata
        self.name = "Temperature and Pressure Module"
        self.version = "1.0.0"
        self.description = "Monitors temperature and pressure sensors"
        
        # Initialize streams
        self.streams = self._initialize_streams()
        
        # Configuration settings
        self.config = {
            'update_rate': 1.0,            # Update rate in seconds
            'temperature_range': {          # Valid temperature range
                'min': -50,
                'max': 150
            },
            'pressure_range': {            # Valid pressure range
                'min': 800,
                'max': 1200
            },
            'enabled_streams': ['stream1', 'stream2'],
            'debug_mode': False
        }
        
        # Module state
        self.running = False
        self.error_count = 0
        self.last_error = None

    def _initialize_streams(self) -> dict:
        """Initialize all module streams with metadata"""
        return {
            'stream1': Stream(
                stream_id=1,
                name="Temperature",
                datatype="float",
                unit="Celsius",
                status="active",
                metadata={
                    "sensor": "TMP36",
                    "precision": 0.1,
                    "location": "main_chamber",
                    "calibration_date": datetime.now().strftime("%Y-%m-%d")
                }
            ),
            'stream2': Stream(
                stream_id=2,
                name="Pressure",
                datatype="float",
                unit="hPa",
                status="active",
                metadata={
                    "sensor": "BMP180",
                    "precision": 0.5,
                    "location": "main_chamber",
                    "calibration_date": datetime.now().strftime("%Y-%m-%d")
                }
            )
        }

    def _generate_sensor_data(self, stream_id: str) -> float:
        """Generate simulated sensor data within configured ranges"""
        if stream_id == 'stream1':  # Temperature
            return random.uniform(
                self.config['temperature_range']['min'],
                self.config['temperature_range']['max']
            )
        elif stream_id == 'stream2':  # Pressure
            return random.uniform(
                self.config['pressure_range']['min'],
                self.config['pressure_range']['max']
            )
        return 0.0

    async def update_streams_forever(self):
        """Main update loop for the module"""
        self.running = True
        
        while self.running:
            try:
                # Update only enabled streams
                for stream_id in self.config['enabled_streams']:
                    if stream_id in self.streams:
                        value = self._generate_sensor_data(stream_id)
                        self.streams[stream_id].update_value(value)
                        
                        if self.config['debug_mode']:
                            print(f"Updated {stream_id}: {value}")
                
                await asyncio.sleep(self.config['update_rate'])
                
            except Exception as e:
                self.error_count += 1
                self.last_error = str(e)
                print(f"Error in update loop: {e}")
                await asyncio.sleep(1)  # Sleep on error to prevent rapid loops

    def get_streams(self) -> dict:
        """Return current stream data"""
        return {stream_id: stream.to_dict() 
                for stream_id, stream in self.streams.items()
                if stream_id in self.config['enabled_streams']}

    def get_status(self) -> dict:
        """Return module status information"""
        return {
            "running": self.running,
            "error_count": self.error_count,
            "last_error": self.last_error,
            "active_streams": len(self.config['enabled_streams']),
            "config": self.config
        }

    def update_config(self, config_key: str, value: any):
        """Update a single configuration value"""
        if config_key in self.config:
            self.config[config_key] = value
            return True
        return False

    def update_multiple_configs(self, config_updates: dict):
        """Update multiple configuration values"""
        for key, value in config_updates.items():
            self.update_config(key, value)

    def control_module(self, command: str, params: dict = None):
        """Handle control commands"""
        commands = {
            "start": self._start_module,
            "stop": self._stop_module,
            "reset": self._reset_module,
            "enable_stream": self._enable_stream,
            "disable_stream": self._disable_stream
        }
        
        if command in commands:
            return commands[command](params)
        else:
            raise ValueError(f"Unknown command: {command}")

    def _start_module(self, params=None):
        """Start the module"""
        self.running = True
        return {"status": "started"}

    def _stop_module(self, params=None):
        """Stop the module"""
        self.running = False
        return {"status": "stopped"}

    def _reset_module(self, params=None):
        """Reset module state"""
        self.error_count = 0
        self.last_error = None
        self.streams = self._initialize_streams()
        return {"status": "reset"}

    def _enable_stream(self, params):
        """Enable a specific stream"""
        if params and 'stream_id' in params:
            stream_id = params['stream_id']
            if stream_id in self.streams and stream_id not in self.config['enabled_streams']:
                self.config['enabled_streams'].append(stream_id)
                return {"status": "enabled", "stream": stream_id}
        return {"status": "error", "message": "Invalid stream_id"}

    def _disable_stream(self, params):
        """Disable a specific stream"""
        if params and 'stream_id' in params:
            stream_id = params['stream_id']
            if stream_id in self.config['enabled_streams']:
                self.config['enabled_streams'].remove(stream_id)
                return {"status": "disabled", "stream": stream_id}
        return {"status": "error", "message": "Invalid stream_id"}

    async def cleanup(self):
        """Cleanup module resources"""
        self.running = False
        # Add any additional cleanup code here