import asyncio
import websockets
import json

async def send_update():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        # Send a stream update
        update_message = json.dumps({
            'type': 'update',
            'stream_id': 'temperature',
            'value': 23.5
        })
        await websocket.send(update_message)

        # Await a response from the server
        response = await websocket.recv()
        print(f"Server response: {response}")

# Start the client
asyncio.run(send_update())
