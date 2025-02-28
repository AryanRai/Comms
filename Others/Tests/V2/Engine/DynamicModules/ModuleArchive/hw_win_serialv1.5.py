import serial
from serial.serialutil import SerialException
import asyncio
import serial.tools.list_ports
from __init__ import Stream
from datetime import datetime

START_MARKER = 0x7E

# ChyappyTransformer class to handle all CHYappy protocol logic
class ChyappyTransformer:
    def __init__(self):
        pass

    def calculate_checksum(self, payload):
        """Calculate the XOR checksum for the given payload."""
        checksum = 0
        for byte in payload:
            checksum ^= byte
        return checksum

    def parse_chyappy(self, data):
        # Check if the first byte is the START_MARKER
        if len(data) < 5 or int(data[0], 16) != START_MARKER:
            print("Invalid CHYappy message: Incorrect start marker or too short")
            return None

        # Extract fields from the data
        length = int(data[1], 16)
        sensor_type = int(data[2], 16)
        sensor_id = int(data[3], 16)

        # Extract payload bytes
        payload_bytes = [int(byte, 16) for byte in data[4:4 + length]]
        # Calculate checksum from payload
        calculated_checksum = self.calculate_checksum(payload_bytes)

        # Check if the last byte is the expected checksum
        received_checksum = int(data[4 + length], 16)
        if calculated_checksum != received_checksum:
            print(f"Checksum error: calculated {calculated_checksum} but received {received_checksum}")
            return None

        # Convert payload bytes to string representation
        payload = ''.join(chr(byte) for byte in payload_bytes)
        return sensor_type, sensor_id, payload

    def process_message(self, sensor_type, sensor_id, payload):
        """Process the received message and print the details."""
        print(f"Received sensor type: {chr(sensor_type)}")
        print(f"Sensor ID: {sensor_id}")
        print(f"Payload (as string): {payload}")
        return sensor_type, sensor_id, payload


# SerialModule class for handling serial communication and updating streams
class hw_win_serial_chyappy:
    def __init__(self, port='COM3', baudrate=115200, Debuglvl=0):
        self.port = port
        self.baudrate = baudrate
        self.Debuglvl = Debuglvl
        self.ser = None
        self.chyappy_parser = ChyappyTransformer()  # Instance of ChyappyTransformer
        self.streams = self._initialize_streams()  # Dictionary of Stream objects

    def _initialize_streams(self) -> dict:
        """Initialize all module streams with metadata"""
        return {
            '1': Stream(
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
            '2': Stream(
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

    def decode_hex_string(self, hex_string):
        """Convert a hex string like '7E:9:54:...' into a split list of string representations of the bytes."""
        try:
            split_data_lst = hex_string.split(":")
            return split_data_lst
        except ValueError:
            print("Error decoding hex string")
            return None

    def read_serial(self):
        """Read raw serial data."""
        if self.ser and self.ser.in_waiting > 0:
            data = self.ser.read_until(b'\n')  # Reading until newline character
            print(f"Raw data received: {data}")  # Print raw data received from serial
            return data
        return None

    async def update_streams_forever(self):
        """Main loop to listen to serial and update engine streams."""
        self.connect()
        while True:
            data = self.read_serial()
            if data:
                hex_string = ""
                if b'7E' in data:  # Assuming the ChYappy messages start with '7E'
                    for byte in data:
                        hex_string += chr(byte)
                    decoded_data = self.decode_hex_string(hex_string)
                    parsed_data = self.chyappy_parser.parse_chyappy(decoded_data)
                    if parsed_data:
                        sensor_type, sensor_id, payload = parsed_data
                        try:
                            # Ensure the payload can be converted to float
                            self.update_streams(sensor_id, float(payload))  # Update streams
                        except ValueError:
                            print(f"Invalid payload for sensor ID {sensor_id}: {payload}")
            await asyncio.sleep(0.1)

    def update_streams(self, sensor_id, value):
        """Update the streams based on sensor ID and value."""
        stream_id_str = str(sensor_id)  # Convert sensor_id to string to match stream keys
        if stream_id_str in self.streams:
            stream = self.streams[stream_id_str]
            stream.update_value(value)
            if self.Debuglvl > 0:
                print(f"Stream {sensor_id} updated with value {value}")
        else:
            print(f"No stream found for sensor ID {sensor_id}")

    def close(self):
        if self.ser:
            self.ser.close()
            print("Closed serial connection")


# Example usage:
async def main():
    serial_module = hw_win_serial_chyappy(port='COM3', baudrate=115200, Debuglvl=1)
    serial_module.list_ports()  # List the available ports

    # Run all tasks concurrently
    await asyncio.gather(
        serial_module.listen_and_update()  # Listen for incoming serial data
    )


if __name__ == "__main__":
    asyncio.run(main())
