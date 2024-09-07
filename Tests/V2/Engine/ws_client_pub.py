# publisher_client.py
import asyncio
import websockets
import json
import random

async def publish_streams():
    uri = "ws://localhost:8765"
    stream_id = "sensor_data"

    while True:
        try:
            # Connect to the WebSocket server with ping_interval=None
            async with websockets.connect(uri, ping_interval=None) as websocket:
                print("Connected to WebSocket server.")

                while True:
                    data = {
                        'type': 'update',
                        'stream_id': stream_id,
                        'value': random.uniform(20.0, 30.0)  # Simulating sensor value
                    }

                    await websocket.send(json.dumps(data))
                    await asyncio.sleep(0.001)  # Update at 1000 Hz

        except (websockets.exceptions.ConnectionClosed, ConnectionRefusedError) as e:
            print(f"Connection lost: {e}. Reconnecting in 5 seconds...")
            await asyncio.sleep(5)
        except Exception as e:
            print(f"Unexpected error: {e}")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(publish_streams())
