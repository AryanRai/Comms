# hw_module_1.py
# v1.0

import asyncio
from datetime import datetime
from __init__ import Stream
import serial

class hw_win_serial_universal:
    """Hardware module with serial data forwarding to a stream."""

    def __init__(self, serial_port="COM4", baud_rate=115200):
        # Module metadata
        self.name = "Serial Data Module"
        self.version = "2.0.0"
        self.description = "Transmits serial data to a dedicated stream"

        # Serial configuration
        self.serial_port = serial_port
        self.baud_rate = baud_rate
        self.serial_connection = None

        # Initialize streams
        self.streams = self._initialize_streams()

        # Configuration settings
        self.config = {
            'update_rate': 0.1,            # Update rate in seconds
            'enabled_streams': ['serial_stream'],
            'debug_mode': True
        }

        # Module state
        self.running = False
        self.error_count = 0
        self.last_error = None

    def _initialize_streams(self) -> dict:
        """Initialize all module streams with metadata"""
        return {
            'serial_stream': Stream(
                stream_id=1,
                name="Serial Data",
                datatype="string",
                unit=None,
                status="active",
                metadata={
                    "source": "serial",
                    "baud_rate": self.baud_rate,
                    "port": self.serial_port,
                    "description": "Raw data received over serial connection"
                }
            )
        }

    async def _read_serial_data(self):
        """Continuously read data from the serial port and send it to the stream."""
        while self.running:
            try:
                if self.serial_connection and self.serial_connection.in_waiting > 0:
                    data = self.serial_connection.readline().decode('utf-8').strip()
                    self.streams['serial_stream'].update_value(data)

                    if self.config['debug_mode']:
                        print(f"Serial Data: {data}")

                await asyncio.sleep(self.config['update_rate'])
            except Exception as e:
                self.error_count += 1
                self.last_error = str(e)
                print(f"Error reading serial data: {e}")
                await asyncio.sleep(1)  # Sleep on error to prevent rapid loops

    async def update_streams_forever(self):
        """Main update loop for the module."""
        self.running = True

        # Attempt to open the serial connection
        try:
            self.serial_connection = serial.Serial(self.serial_port, self.baud_rate, timeout=1)
            print(f"Serial connection established on {self.serial_port} at {self.baud_rate} baud.")
        except Exception as e:
            self.error_count += 1
            self.last_error = str(e)
            print(f"Failed to open serial connection: {e}")
            self.running = False
            return

        # Start reading serial data
        await self._read_serial_data()

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

    async def cleanup(self):
        """Cleanup module resources"""
        self.running = False
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            print("Serial connection closed.")
