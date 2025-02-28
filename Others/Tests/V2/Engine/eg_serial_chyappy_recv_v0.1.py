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
