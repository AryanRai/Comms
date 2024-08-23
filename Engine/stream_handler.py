import asyncio
import websockets
import json

# This dictionary will hold the current state of the streams
streams = {}

async def stream_handler(websocket, path):
    async for message in websocket:
        # Assume the message is a JSON string, parse it
        data = json.loads(message)

        if data['type'] == 'update':
            # Update the stream value
            stream_id = data['stream_id']
            streams[stream_id] = data['value']
            print(f"Updated stream {stream_id} with value: {data['value']}")

            # Optionally, send a confirmation back to the sender
            await websocket.send(json.dumps({
                'status': 'ok',
                'stream_id': stream_id,
                'value': streams[stream_id]
            }))
        elif data['type'] == 'fetch':
            # Fetch and send the current value of a specific stream
            stream_id = data['stream_id']
            value = streams.get(stream_id, None)
            await websocket.send(json.dumps({
                'stream_id': stream_id,
                'value': value
            }))

# Start the WebSocket server
async def start_server():
    async with websockets.serve(stream_handler, "localhost", 8765):
        print("WebSocket server started on ws://localhost:8765")
        await asyncio.Future()  # Keep the server running

# Start the server in an asyncio loop
if __name__ == "__main__":
    asyncio.run(start_server())
