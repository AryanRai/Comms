# subscriber_client.py
import asyncio
import websockets
import json

async def subscribe_and_fetch():
    uri = "ws://localhost:8765"  # Connect to the WebSocket server
    async with websockets.connect(uri, ping_interval=None, ping_timeout=None) as websocket:
        # Send a request to fetch a stream value
        fetch_message = json.dumps({
            'type': 'fetch',
            'stream_id': 'sensor_data'  # Stream ID we want to fetch
        })
        await websocket.send(fetch_message)

        # Receive the fetched value
        response = await websocket.recv()
        print(f"Initial fetch response: {response}")

        # Now subscribe to receive updates
        while True:
            # Continuously receive and print updates from the server
            message = await websocket.recv()
            data = json.loads(message)
            print(f"Received update: {data['stream_id']} -> {data['value']:.2f}")

# Start the client
if __name__ == "__main__":
    asyncio.run(subscribe_and_fetch())
