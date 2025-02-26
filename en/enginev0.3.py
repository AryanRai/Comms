import asyncio
import aiohttp
import json
from datetime import datetime


class Stream:
    def __init__(self, stream_id, datatype, unit, status, metadata):
        self.data = {
            "stream_id": stream_id,
            "datatype": datatype,
            "unit": unit,
            "status": status,
            "metadata": metadata,
            "value": 0,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
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


class Engine:
    def __init__(self, Debuglvl=0):
        self.value = 0
        self.Debuglvl = Debuglvl
        self.streams = {
            "stream1": Stream(stream_id="stream1", datatype="float", unit="bar", status="active", metadata={}),
            "stream2": Stream(stream_id="stream2", datatype="float", unit="bar", status="active", metadata={})
        }

    async def test_update_value(self, rate):
        while True:
            self.value += 1  # Increment the value
            self.streams["stream1"].update_value(self.value)
            self.streams["stream2"].update_value(self.value)

            if self.Debuglvl > 1:
                print("Engine: Simulated Data Update:", {k: v.to_dict() for k, v in self.streams.items()})

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

                    # Serialize engine's stream data for sending
                    stream_data = {k: v.to_dict() for k, v in self.engine.streams.items()}
                    negotiation = {
                        "type": "negotiation",
                        "status": "active",
                        "data": stream_data
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
