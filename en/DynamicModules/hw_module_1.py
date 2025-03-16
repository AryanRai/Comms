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
        
        # Configuration settings - Initialize this FIRST
        self.config = {
            'update_rate': 0.1,            # Update rate in seconds (100ms)
            'temperature_range': {          # Valid temperature range
                'min': -50,
                'max': 150
            },
            'pressure_range': {            # Valid pressure range
                'min': 800,
                'max': 1200
            },
            'enabled_streams': ['stream1', 'stream2'],
            'debug_mode': True,
            'notify_on_change': True       # Enable change notifications
        }
        
        # Initialize streams AFTER config
        self.streams = self._initialize_streams()
        
        # Module state
        self.running = False
        self.error_count = 0
        self.last_error = None
        self.debug_messages = []
        self.value_change_history = []  # Track value changes

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
                    "calibration_date": datetime.now().strftime("%Y-%m-%d"),
                    "range": {
                        "min": self.config['temperature_range']['min'],
                        "max": self.config['temperature_range']['max']
                    },
                    "step": 0.1
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
                    "calibration_date": datetime.now().strftime("%Y-%m-%d"),
                    "range": {
                        "min": self.config['pressure_range']['min'],
                        "max": self.config['pressure_range']['max']
                    },
                    "step": 1.0
                }
            )
        }

    def _handle_value_change(self, stream_id: str, old_value: float, new_value: float, source: str = "internal"):
        """Handle value changes and generate notifications"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        
        # Ensure values are floats
        try:
            old_value = float(old_value)
            new_value = float(new_value)
        except (TypeError, ValueError):
            old_value = 0.0
            new_value = 0.0
        
        # Create change record
        change_record = {
            "timestamp": timestamp,
            "stream_id": stream_id,
            "old_value": old_value,
            "new_value": new_value,
            "source": source,
            "stream_name": self.streams[stream_id].data["name"] if stream_id in self.streams else "Unknown"
        }
        
        # Add to history
        self.value_change_history.append(change_record)
        if len(self.value_change_history) > 100:  # Keep last 100 changes
            self.value_change_history.pop(0)
        
        # Generate notification message
        message = f"[{timestamp}] {change_record['stream_name']} ({stream_id}) changed from {old_value} to {new_value} [{source}]"
        print(f"Module hw_module_1: {message}")
        self.debug_messages.append(message)
        if len(self.debug_messages) > 100:
            self.debug_messages.pop(0)
        
        return change_record

    def _generate_sensor_data(self, stream_id: str) -> float:
        """Generate simulated sensor data within configured ranges"""
        try:
            old_value = float(self.streams[stream_id].data["value"]) if stream_id in self.streams else 0.0
        except (TypeError, ValueError):
            old_value = 0.0
        
        if stream_id == 'stream1':  # Temperature
            new_value = random.uniform(
                float(self.config['temperature_range']['min']),
                float(self.config['temperature_range']['max'])
            )
        elif stream_id == 'stream2':  # Pressure
            new_value = random.uniform(
                float(self.config['pressure_range']['min']),
                float(self.config['pressure_range']['max'])
            )
        else:
            new_value = 0.0
            
        # Handle value change notification for internal updates
        if self.config['notify_on_change'] and abs(float(new_value) - float(old_value)) > 0.001:
            self._handle_value_change(stream_id, old_value, new_value, source="internal")
            
        return float(new_value)

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
            # Check if this is a stream value update
            if key.endswith('_value'):
                stream_id = key.replace('_value', '')
                if stream_id in self.streams:
                    try:
                        old_value = float(self.streams[stream_id].data["value"])
                        new_value = float(value)
                    except (TypeError, ValueError):
                        old_value = 0.0
                        new_value = 0.0
                        
                    self.streams[stream_id].update_value(new_value)
                    
                    # Handle the value change notification
                    if self.config['notify_on_change']:
                        self._handle_value_change(stream_id, old_value, new_value, source="UI")
            else:
                self.update_config(key, value)

    def control_module(self, command: str):
        """Handle control commands"""
        commands = {
            "start": self._start_module,
            "stop": self._stop_module,
            "reset": self._reset_module,
            "enable_stream": self._enable_stream,
            "disable_stream": self._disable_stream,
            "set_high": self._set_high,
            "set_low": self._set_low
        }
        
        if command in commands:
            return commands[command]()
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

    def _set_high(self, params=None):
        """Set output high (1)"""
        for stream_id in self.config['enabled_streams']:
            if stream_id in self.streams:
                self.streams[stream_id].update_value(1)
        return {"status": "set_high"}

    def _set_low(self, params=None):
        """Set output low (0)"""
        for stream_id in self.config['enabled_streams']:
            if stream_id in self.streams:
                self.streams[stream_id].update_value(0)
        return {"status": "set_low"}

    async def cleanup(self):
        """Cleanup module resources"""
        self.running = False
        # Add any additional cleanup code here

    def log_stream_update(self, stream_id: str, value: float):
        """Log stream value updates"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        message = f"[{timestamp}] Stream {stream_id} updated to {value}"
        print(f"Module hw_module_1: {message}")
        self.debug_messages.append(message)
        if len(self.debug_messages) > 100:  # Keep last 100 messages
            self.debug_messages.pop(0)

    def log_control_command(self, command: str):
        """Log control commands"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        message = f"[{timestamp}] Received control command: {command}"
        print(f"Module hw_module_1: {message}")
        self.debug_messages.append(message)
        if len(self.debug_messages) > 100:  # Keep last 100 messages
            self.debug_messages.pop(0)

    def get_debug_messages(self):
        """Return recent debug messages"""
        return self.debug_messages

    def get_value_changes(self, limit: int = 10) -> list:
        """Get recent value changes with optional limit"""
        return self.value_change_history[-limit:]