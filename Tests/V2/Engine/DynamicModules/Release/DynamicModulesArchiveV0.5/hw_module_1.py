# hw_module_1.py

import random
import asyncio
from __init__ import Stream  # Adjusted import statement for the Stream class
from datetime import datetime

class hw_module_1:
    def __init__(self):
        # Define streams using the Stream class
        self.streams = {
            'stream1': Stream(stream_id=1, name="Temperature", datatype="float", unit="Celsius", status="active", metadata={"sensor": "TMP36"}),
            'stream2': Stream(stream_id=2, name="Pressure", datatype="float", unit="Pascal", status="active", metadata={"sensor": "BMP180"})
        }

        # Configuration dictionary to store settings like rate
        self.config = {
            'rate': 1,  # Default update rate
            'other_config': 'default_value'  # Other configurations can be added here
        }

    async def update_streams_forever(self):
        """Continuously update the streams with random data."""
        while True:
            # Update streams with random values
            self.streams['stream1'].update_value(random.uniform(0, 100))
            self.streams['stream2'].update_value(random.uniform(0, 100))

            # Sleep for the rate specified in the config
            await asyncio.sleep(self.config['rate'])

    def get_streams(self):
        """Return the current values of the streams as dictionaries."""
        return {stream_id: stream.to_dict() for stream_id, stream in self.streams.items()}

    def set_stream(self, stream_id, value):
        """Set the value of a specific stream from the external (stream handler)."""
        if stream_id in self.streams:
            self.streams[stream_id].update_value(value)
            print(f"HWModule1 stream {stream_id} set to: {value}")
        else:
            print(f"HWModule1 stream {stream_id} not found.")

    def control_module(self, command):
        """Handle control commands from the external (stream handler)."""
        print(f"Received control command: {command}")

    # New methods for config handling
    def get_config(self):
        """Return the current configuration."""
        return self.config

    def update_config(self, config_key, value):
        """Update a specific configuration setting."""
        if config_key in self.config:
            self.config[config_key] = value
            print(f"Configuration '{config_key}' updated to: {value}")
        else:
            print(f"Configuration '{config_key}' not found.")

    def update_multiple_configs(self, config_updates):
        """Update multiple configuration settings."""
        for key, value in config_updates.items():
            if key in self.config:
                self.config[key] = value
                print(f"Configuration '{key}' updated to: {value}")
            else:
                print(f"Configuration '{key}' not found.")
