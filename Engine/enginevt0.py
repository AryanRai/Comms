#the engine has modules that can be installed for specific types of hardware like sensors and for example can communicate using serial or different kinds of methods which u dont need to worry about
#the modules create streams for each variable a hardware has and constantly updates these values through the engine within the stream handler

#the engine handles the modules and get data to publish the data to the websocket server and receiving data from the websocket server to send back to the modules



#ahh yes the negotiator.
#The negotiator is a class, this is the link between the engine and the stream handler which is responsible for publishing data from HW modules to the steam handler and receiving data from the stream handler send back to HW modules. 



#The engine itself handles all the module processes, where each module is another python file with the class a list of streams from and the to module that can be interpreted automatically by the engine

import os
import importlib
import asyncio
import aiohttp
import json
from datetime import datetime
import random
#ahh yes the negotiator
class Negotiator:
    """Handles communication between the engine and the WebSocket stream handler using aiohttp."""

    def __init__(self, ws_url='ws://localhost:3000'):
        self.ws_url = ws_url
        self.data = {
            "stream1": {
                "stream_id": "temperature",
                "datatype": "float",
                "unit": "Celsius",
                "status": "active",
                "metadata": {
                    "sensor_id": "A1234",
                    "location": "Room 1",
                    "calibration_date": "2024-09-16"
                },
                "value": 0,
                "timestamp": "",
                "priority": "high"
            },
            "stream2": {
                "stream_id": "pressure",
                "datatype": "float",
                "unit": "bar",
                "status": "active",
                "value": 0,
                "timestamp": "",
                "priority": "high"
            }
        }

    # Function to continuously publish messages to the WebSocket server
    async def pub_sub(self, rate=0.01):  # Adjust rate to control message frequency
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(self.ws_url) as ws:
                self.ws_session = ws
                message_count = 0

                                
                while True:


                    negotiation = {
                    "type": "negotiation",
                    "status": "active",
                        "data": self.data
                    }
                    message = json.dumps(negotiation)
                    
                    # Send the message
                    await ws.send_str(message)
                    #print(f"Sent: {message}")

                    # Optional: Receive a response from the server
                    response = await ws.receive()
                    #print(f"Received: {response.data}")

                    message_count += 1

                    # Sleep for a short time to simulate message frequency
                    await asyncio.sleep(rate)


    async def close(self):
        """Close the aiohttp ClientSession."""
        await self.ws_session.close()


    # You can add a method to update data if needed
    def update_data(self, stream_id, key, value):
        if stream_id in self.data:
            self.data[stream_id][key] = value


class ModuleHandler:
    """Handles loading HW modules and communicating with the WebSocket via the Negotiator."""


    def load_modules(self):
        """Dynamically load all hardware modules from the 'modules' folder."""


    async def run(self):
        """Run the engine to handle HW modules and streams."""


    async def cleanup(self):
        """Cleanup resources."""

    
class Engine:
    """Handles value updates and stream handling."""

    def __init__(self, negotiator: Negotiator, module_handler: ModuleHandler):
        self.negotiator = negotiator
        self.module_handler = module_handler
        

    async def run(self):
        """Run the engine to handle HW modules and streams."""
        #await self.module_handler.run()
       

    async def cleanup(self):
        """Cleanup resources."""
    
    async def update_values(self):
        """Update values from the negotiator."""
        # Update values test
        while True: 
            self.negotiator.data["stream1"]["value"] = random.randint(0, 100)
            self.negotiator.data["stream1"]["timestamp"] = datetime.now().isoformat()
            self.negotiator.data["stream2"]["value"] = random.randint(0, 100)
            self.negotiator.data["stream2"]["timestamp"] = datetime.now().isoformat()

            print(self.negotiator.data)
            await asyncio.sleep(1)





# Entry point to run the publisher
if __name__ == "__main__":
    negotiator = Negotiator()
    module_handler = ModuleHandler()
    engine = Engine(negotiator, module_handler)

    asyncio.run(negotiator.pub_sub(rate=0.01))
    asyncio.run(engine.run())  # Adjust the rate to test different frequencies
    asyncio.run(engine.update_values())




'''

Negotiation data format:

{
    "type": "negotiation",
    "status": "active",
    "data": {}
}


Stream data format:

{
    "type": "update",
    "module": "sensor_module_1",
    "stream_id": "temperature",
    "timestamp": 1694803921,
    "priority": "high",
    "value": 22.5,
    "datatype": "float",
    "unit": "Celsius",
    "status": "active",
    "metadata": {
        "sensor_id": "A1234",
        "location": "Room 1",
        "calibration_date": "2024-09-16"
    }
}


'''