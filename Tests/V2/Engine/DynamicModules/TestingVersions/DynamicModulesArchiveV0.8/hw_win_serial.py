import serial
from serial.serialutil import SerialException
import asyncio
import serial.tools.list_ports

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
        if len(data) < 5 or int(data[0], 16) != START_MARKER:
            print("Invalid CHYappy message: Incorrect start marker or too short")
            return None

        length = int(data[1], 16)
        sensor_type = int(data[2], 16)
        sensor_id = int(data[3], 16)

        payload_bytes = [int(byte, 16) for byte in data[4:4 + length]]
        calculated_checksum = self.calculate_checksum(payload_bytes)

        received_checksum = int(data[4 + length], 16)
        if calculated_checksum != received_checksum:
            print(f"Checksum error: calculated {calculated_checksum} but received {received_checksum}")
            return None

        payload = ''.join(chr(byte) for byte in payload_bytes)
        return sensor_type, sensor_id, payload

    def process_message(self, sensor_type, sensor_id, payload):
        #print(f"Received sensor type: {chr(sensor_type)}")
        #print(f"Sensor ID: {sensor_id}")
        #print("Payload (as string):", payload)
        pass


# hw_win_serial class following your module format
class hw_win_serial:
    def __init__(self, port='COM3', baudrate=115200, debug_lvl=0):
        self.port = port
        self.baudrate = baudrate
        self.debug_lvl = debug_lvl
        self.ser = None
        self.chyappy_parser = ChyappyTransformer()  # Instance of ChyappyTransformer

        # Initialize streams
        self.streams = {
            'sensor_type': None,
            'sensor_id': None,
            'payload': None
        }

    def list_ports(self):
        """List available serial ports."""
        ports = serial.tools.list_ports.comports()
        available_ports = [port.device for port in ports]
        active_ports = [port.device for port in ports if port]
        print("Available ports:", available_ports)
        print("Active ports:", active_ports)
        return available_ports

    def connect(self):
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
            if self.debug_lvl > 0:
                print(f"Connected to serial port: {self.port} at baudrate: {self.baudrate}")
        except SerialException as e:
            print(f"Failed to connect to serial port: {e}")

    def decode_hex_string(self, hex_string):
        """Convert a hex string into a list of string representations of the bytes."""
        try:
            split_data_lst = hex_string.split(":")
            return split_data_lst
        except ValueError:
            print("Error decoding hex string")
            return None

    def read_serial(self):
        if self.ser and self.ser.in_waiting > 0:
            data = self.ser.read_until(b'\n')  # Reading until newline character
            return data
        return None

    async def update_streams_forever(self, rate=0.1):
        """Main loop to listen to serial and update streams."""
        self.connect()
        while True:
            data = self.read_serial()
            if data:
                hex_string = ""
                if b'7E' in data:  # Assuming CHYappy messages start with '7E'
                    for byte in data:
                        hex_string += chr(byte)
                    decoded_data = self.decode_hex_string(hex_string)
                    parsed_data = self.chyappy_parser.parse_chyappy(decoded_data)
                    if parsed_data:
                        sensor_type, sensor_id, payload = parsed_data
                        self.chyappy_parser.process_message(sensor_type, sensor_id, payload)
                        
                        # Update streams with parsed data
                        self.streams['sensor_type'] = sensor_type
                        self.streams['sensor_id'] = sensor_id
                        self.streams['payload'] = payload

            await asyncio.sleep(rate)

    def get_streams(self):
        """Return the current values of the streams."""
        return self.streams

    def set_stream(self, stream_id, value):
        """Set the value of a specific stream."""
        if stream_id in self.streams:
            self.streams[stream_id] = value
            print(f"SerialModule stream {stream_id} set to: {value}")
        else:
            print(f"SerialModule stream {stream_id} not found.")

    def control_module(self, command):
        """Handle control commands."""
        print(f"Received control command: {command}")

    def close(self):
        if self.ser:
            self.ser.close()
            print("Closed serial connection")


# Example usage:
if __name__ == "__main__":
    serial_module = hw_win_serial(port='COM3', baudrate=115200, debug_lvl=1)
    asyncio.run(serial_module.update_streams_forever())
