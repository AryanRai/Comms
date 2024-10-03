import asyncio
import aiohttp
import json
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
        self.data["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

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


class Module:
    def __init__(self, module_id, name, streams):
        self.module_id = module_id
        self.name = name
        # Streams will be a dictionary of stream_id -> Stream objects
        self.streams = {stream.stream_id: stream for stream in streams}

    def update_stream_value(self, stream_id, value):
        if stream_id in self.streams:
            self.streams[stream_id].update_value(value)

    def to_dict(self):
        return {
            "module_id": self.module_id,
            "name": self.name,
            "streams": {k: v.to_dict() for k, v in self.streams.items()}
        }


class Engine:
    def __init__(self, Debuglvl=0):
        self.value = 0
        self.Debuglvl = Debuglvl
        # Engine will now manage multiple modules, each with its own streams
        self.modules = {
            "module1": Module(
                module_id="module1", name="SensorModule1",
                streams=[
                    Stream(stream_id="stream1", name="stream1", datatype="float", unit="bar", status="active", metadata={}),
                    Stream(stream_id="stream2", name="stream2", datatype="float", unit="bar", status="active", metadata={})
                ]
            ),
            "module2": Module(
                module_id="module2", name="SensorModule2",
                streams=[
                    Stream(stream_id="stream3", name="stream3", datatype="int", unit="psi", status="active", metadata={}),
                    Stream(stream_id="stream4", name="stream4", datatype="int", unit="psi", status="active", metadata={})
                ]
            )
        }

    async def test_update_value(self, rate):
        while True:
            self.value += 1  # Increment the value

            # Update stream values for all modules
            for module in self.modules.values():
                for stream_id in module.streams:
                    module.update_stream_value(stream_id, self.value)

            if self.Debuglvl > 1:
                print("Engine: Simulated Data Update:")
                for module_id, module in self.modules.items():
                    print(f"Module {module_id}: {module.to_dict()}")

            await asyncio.sleep(rate)


class Negotiator:
    def __init__(self, engine, ws_url='ws://localhost:3000', Debuglvl=0):
        self.engine = engine
        self.ws_url = ws_url
        self.Debuglvl = Debuglvl

    async def test_pub_sub(self, rate):
        while True:
            if self.Debuglvl > 0:
                print(f"Current value: {self.engine.value}")
            await asyncio.sleep(rate)

    async def ws_pub_sub(self, rate):
        if self.Debuglvl > 0:
            print("Starting pub_sub")

        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(self.ws_url) as ws:
                self.ws_session = ws
                message_count = 0

                while True:
                    if self.Debuglvl > 0:
                        print("Negotiator: Sending WS message")

                    # Serialize engine's module and stream data for sending
                    module_data = {module_id: module.to_dict() for module_id, module in self.engine.modules.items()}
                    negotiation = {
                        "type": "negotiation",
                        "status": "active",
                        "data": module_data,
                        "msg-sent-timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    }

                    message = json.dumps(negotiation)

                    # Send the message
                    await ws.send_str(message)
                    if self.Debuglvl > 1:
                        print(f"Negotiator: Sent: {message}")

                    # Optional: Receive a response from the server
                    response = await ws.receive()
                    if self.Debuglvl > 1:
                        print(f"Negotiator: Received WS: {response.data}")

                    message_count += 1

                    # Sleep for a short time to simulate message frequency
                    await asyncio.sleep(rate)

    async def close(self):
        """Close the aiohttp ClientSession."""
        if self.Debuglvl > 0:
            print("Negotiator: Closing websocket client")
        await self.ws_session.close()


class ModuleHandler:
    """Handles loading HW modules and communicating with the WebSocket via the Negotiator."""

    def __init__(self, Debuglvl=0):
        self.Debuglvl = Debuglvl

    def load_modules(self):
        """Dynamically load all hardware modules from the 'modules' folder."""
        pass

    async def run(self):
        """Run the engine to handle HW modules and streams."""
        while True:
            if self.Debuglvl > 0:
                print("ModuleHandler running...")
            await asyncio.sleep(1)

    async def cleanup(self):
        """Cleanup resources."""
        pass


# Main function that sets up and runs both loops concurrently using asyncio
async def main():
    engine = Engine(Debuglvl=1)  # Create updater object
    negotiator = Negotiator(engine, ws_url='ws://localhost:3000', Debuglvl=1)  # Pass updater to the printer
    module_handler = ModuleHandler(Debuglvl=1)

    # Run both tasks (coroutines) concurrently
    await asyncio.gather(
        engine.test_update_value(0.01),
        negotiator.test_pub_sub(0.01),
        negotiator.ws_pub_sub(0.01),
        module_handler.run()
    )


# Run the asyncio event loop
if __name__ == "__main__":
    asyncio.run(main())
