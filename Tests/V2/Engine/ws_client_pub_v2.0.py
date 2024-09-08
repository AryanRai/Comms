import asyncio
import aiohttp
import json

# Function to continuously publish messages to the WebSocket server
async def publish(rate=0.01):  # Adjust rate to control message frequency
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect('ws://localhost:3000') as ws:
            message_count = 0
            while True:
                # Create a JSON message
                message = json.dumps({
                    'type': 'update',
                    'stream_id': 'test_stream',
                    'value': message_count
                })
                
                # Send the message
                await ws.send_str(message)
                print(f"Sent: {message}")

                # Optional: Receive a response from the server
                response = await ws.receive()
                print(f"Received: {response.data}")

                message_count += 1

                # Sleep for a short time to simulate message frequency
                await asyncio.sleep(rate)

# Entry point to run the publisher
if __name__ == "__main__":
    asyncio.run(publish(rate=0.01))  # Adjust the rate to test different frequencies
