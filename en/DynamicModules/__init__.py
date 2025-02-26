from datetime import datetime

class Stream:
    def __init__(self, stream_id, name, datatype, unit, status, metadata, debug_level=0):
        self.stream_id = stream_id  # Assign stream_id to the object
        self.debug_level = debug_level  # Set debug level
        self.data = {  # Initialize data dictionary
            "stream_id": stream_id,
            "name": name,
            "datatype": datatype,
            "unit": unit,
            "status": status,
            "metadata": metadata,
            "value": '',
            "stream-update-timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "priority": "high"
        }
        if self.debug_level >= 1:
            print(f"Stream initialized with ID: {stream_id}, Name: {name}, Datatype: {datatype}, Unit: {unit}, Status: {status}")

    def update_value(self, value):
        if self.debug_level >= 1:
            print(f"Updating value to: {value}")
        self.data["value"] = value
        self.data["stream-update-timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if self.debug_level == 2:
            print(f"Value updated. Current data: {self.data}")

    def update_metadata(self, metadata):
        if self.debug_level >= 1:
            print(f"Updating metadata to: {metadata}")
        self.data["metadata"] = metadata
        if self.debug_level == 2:
            print(f"Metadata updated. Current data: {self.data}")

    def update_priority(self, priority):
        if self.debug_level >= 1:
            print(f"Updating priority to: {priority}")
        self.data["priority"] = priority
        if self.debug_level == 2:
            print(f"Priority updated. Current data: {self.data}")

    def update_status(self, status):
        if self.debug_level >= 1:
            print(f"Updating status to: {status}")
        self.data["status"] = status
        if self.debug_level == 2:
            print(f"Status updated. Current data: {self.data}")

    def update_datatype(self, datatype):
        if self.debug_level >= 1:
            print(f"Updating datatype to: {datatype}")
        self.data["datatype"] = datatype
        if self.debug_level == 2:
            print(f"Datatype updated. Current data: {self.data}")

    def update_unit(self, unit):
        if self.debug_level >= 1:
            print(f"Updating unit to: {unit}")
        self.data["unit"] = unit
        if self.debug_level == 2:
            print(f"Unit updated. Current data: {self.data}")

    def to_dict(self):
        if self.debug_level >= 1:
            print("Converting stream data to dictionary")
        return self.data