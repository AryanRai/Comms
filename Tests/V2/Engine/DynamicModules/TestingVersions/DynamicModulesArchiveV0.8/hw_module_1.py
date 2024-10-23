# hw_module_1.py

import random
import asyncio

class hw_module_1:
    def __init__(self):
        self.streams = {
            'stream1': 0,
            'stream2': 0
        }

    async def update_streams_forever(self, rate):
        """Continuously update the streams with random data."""
        while True:
            self.streams['stream1'] = random.uniform(0, 100)
            self.streams['stream2'] = random.uniform(0, 100)
            #print(f"HWModule1 streams updated: {self.streams}")
            await asyncio.sleep(rate)  # Sleep for the specified rate

    def get_streams(self):
        """Return the current values of the streams."""
        return self.streams

    def set_stream(self, stream_id, value):
        """Set the value of a specific stream from the external (stream handler)."""
        if stream_id in self.streams:
            self.streams[stream_id] = value
            print(f"HWModule1 stream {stream_id} set to: {value}")
        else:
            print(f"HWModule1 stream {stream_id} not found.")

    def control_module(self, command):
        """Handle control commands from the external (stream handler)."""
        print(f"Received control command: {command}")
    