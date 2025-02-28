# Stream.py

from datetime import datetime

class Stream:
    def __init__(self, stream_id, name, datatype, unit, status, metadata):
        self.stream_id = stream_id  # Assign stream_id to the object
        self.data = {  # Initialize data dictionary
            "stream_id": stream_id,
            "name": name,
            "datatype": datatype,
            "unit": unit,
            "status": status,
            "metadata": metadata,
            "value": 0,
            "stream-update-timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "priority": "high"
        }

    def update_value(self, value):
        self.data["value"] = value
        self.data["stream-update-timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def update_metadata(self, metadata):
        self.data["metadata"] = metadata

    def update_priority(self, priority):
        self.data["priority"] = priority

    def update_status(self, status):
        self.data["status"] = status

    def update_datatype(self, datatype):
        self.data["datatype"] = datatype

    def update_unit(self, unit):
        self.data["unit"] = unit

    def to_dict(self):
        return self.data


