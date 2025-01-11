import serial
from serial.serialutil import SerialException
import asyncio
import serial.tools.list_ports
from __init__ import Stream
from datetime import datetime

class CANBusTransformer:
    def __init__(self):
        pass

    def parse_can_message(self, data):
        """
        Parse a CAN bus message in the format:
        Standard ID: 0x100       DLC: 8  Data: 0x74 0x01 0x02 0x03 0x04 0x05 0x06 0x07
        """
        try:
            data = data.strip()
            if not data.startswith("Standard ID:"):
                print("Invalid CAN message format")
                return None

            parts = data.split()
            std_id = parts[2]
            dlc = int(parts[4])
            data_bytes = [int(byte, 16) for byte in parts[6:6 + dlc]]

            return {
                "std_id": std_id,
                "dlc": dlc,
                "data": data_bytes
            }
        except Exception as e:
            print(f"Error parsing CAN message: {e}")
            return None


class hw_win_serial_canbus:
    def __init__(self, port='COM4', baudrate=115200, Debuglvl=0):
        self.port = port
        self.baudrate = baudrate
        self.Debuglvl = Debuglvl
        self.ser = None
        self.streams = self._initialize_streams()  # Dictionary of Stream objects

    def _initialize_streams(self) -> dict:
        """Initialize all module streams with metadata."""
        return {
            'relay': Stream(
                stream_id=0,
                name="CAN Relay Stream",
                datatype="string",
                unit="message",
                status="active",
                metadata={
                    "description": "Relays all received CAN messages",
                    "created_date": datetime.now().strftime("%Y-%m-%d")
                }
            ),
        }

    def list_ports(self):
        """List available serial ports."""
        ports = serial.tools.list_ports.comports()
        available_ports = [port.device for port in ports]
        print("Available ports:", available_ports)
        return available_ports

    def connect(self):
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
            if self.Debuglvl > 0:
                print(f"Connected to serial port: {self.port} at baudrate: {self.baudrate}")
        except SerialException as e:
            print(f"Failed to connect to serial port: {e}")

    def read_serial(self):
        """Read raw serial data and forward to relay stream."""
        if self.ser and self.ser.in_waiting > 0:
            data = self.ser.readline().decode('utf-8').strip()  # Read and decode the message
            if self.Debuglvl > 0:
                print(f"Raw CAN message received: {data}")
            self.update_streams('relay', data)  # Forward message to relay stream
            return data
        return None

    async def update_streams_forever(self):
        """Main loop to listen to serial and update streams."""
        self.connect()
        while True:
            data = self.read_serial()
            if data:
                # Optionally, process data for other streams here
                pass
            await asyncio.sleep(0.1)

    def update_streams(self, stream_id, value):
        """Update the streams based on stream ID and value."""
        stream_id_str = str(stream_id)  # Convert stream_id to string to match stream keys
        if stream_id_str in self.streams:
            stream = self.streams[stream_id_str]
            stream.update_value(value)
            if self.Debuglvl > 0:
                print(f"Stream {stream_id} updated with value: {value}")
        else:
            print(f"No stream found for stream ID {stream_id}")

    def close(self):
        if self.ser:
            self.ser.close()
            print("Closed serial connection")


# Example usage:
async def main():
    serial_module = hw_win_serial_canbus(port='COM11', baudrate=115200, Debuglvl=1)
    serial_module.list_ports()  # List the available ports

    # Run the update loop
    await asyncio.gather(
        serial_module.update_streams_forever()
    )


if __name__ == "__main__":
    asyncio.run(main())
