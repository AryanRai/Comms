import serial
from serial.serialutil import SerialException  # Importing SerialException directly
import asyncio
import serial.tools.list_ports  # for listing ports

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
            print("Checksum error: calculated {} but received {}".format(calculated_checksum, received_checksum))
            return None

        # Convert payload bytes to string representation
        payload = ''.join(chr(byte) for byte in payload_bytes)
        return sensor_type, sensor_id, payload

    def process_message(self, sensor_type, sensor_id, payload):
        """Process the received message and print the details."""
        # Print the sensor type, sensor ID, and payload
        print(f"Received sensor type: {chr(sensor_type)}")
        print(f"Sensor ID: {sensor_id}")
        print("Payload (as string):", payload)


# SerialModule class for handling serial communication
class SerialModule:
    def __init__(self, port='COM3', baudrate=115200, Debuglvl=0):
        self.port = port
        self.baudrate = baudrate
        self.Debuglvl = Debuglvl
        self.ser = None
        self.chyappy_parser = ChyappyTransformer()  # Instance of ChyappyTransformer

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
            if self.Debuglvl > 0:
                print(f"Connected to serial port: {self.port} at baudrate: {self.baudrate}")
        except SerialException as e:
            print(f"Failed to connect to serial port: {e}")

    def decode_hex_string(self, hex_string):
        """Convert a hex string like '7E:9:54:...' into a split list of string representations of the bytes so 7E:9:54 becomes ['7E', '9', '54']"""
        try: 
            split_data_lst = hex_string.split(":")
            print("decoded data", split_data_lst)
            return split_data_lst

        except ValueError:
            print("Error decoding hex string")
            return None
    
    def read_serial(self):
        if self.ser and self.ser.in_waiting > 0:
            data = self.ser.read_until(b'\n')  # Reading until newline character for this example
            print(f"Raw data received: {data}")  # Print raw data received from serial
            return data
        return None


    async def listen_and_update(self):
        """Main loop to listen to serial and update engine streams."""
        self.connect()
        while True:
            data = self.read_serial()
            if data:
                # Modify this condition to check if ChYappy format is recognized
                hex_string = ""
                # Check if the message is a hex string and decode it
                if b'7E' in data:  # Assuming the ChYappy messages start with '7E'
                    print("ChYappy data detected:", {data})
                    for int in data:
                        #print(chr(int))
                        hex_string += chr(int)
                    decoded_data = self.decode_hex_string(hex_string)
                    parsed_data = self.chyappy_parser.parse_chyappy(decoded_data)  # Use ChyappyParser
                    if parsed_data:
                        sensor_type, sensor_id, payload = parsed_data
                        self.chyappy_parser.process_message(sensor_type, sensor_id, payload)  # Process message
                else:
                    print("Non-ChYappy data detected.")
            await asyncio.sleep(0.1)  # To prevent tight looping

    def close(self):
        if self.ser:
            self.ser.close()
            print("Closed serial connection")


# Updating the main function to include SerialModule
async def main():
    serial_module = SerialModule(port='COM3', baudrate=115200, Debuglvl=1)  # Serial module for ESP32 LoRa
    serial_module.list_ports()  # List the available ports

    # Run all tasks concurrently
    await asyncio.gather(
        serial_module.listen_and_update()  # Listen for incoming serial data
    )


if __name__ == "__main__":
    asyncio.run(main())
