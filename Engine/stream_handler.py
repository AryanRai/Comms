# server.py
import asyncio
import websockets
import json

# This dictionary will hold the current state of the streams
streams = {}
connected_clients = set()

async def stream_handler(websocket, path):
    # Register new client connection
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            data = json.loads(message)

            if data['type'] == 'update':
                stream_id = data['stream_id']
                streams[stream_id] = data['value']
                print(f"Updated stream {stream_id} with value: {data['value']}")

                # Send confirmation back to the sender
                await websocket.send(json.dumps({
                    'status': 'ok',
                    'stream_id': stream_id,
                    'value': streams[stream_id]
                }))

                # Broadcast the updated stream to all other clients
                for client in connected_clients:
                    if client != websocket:
                        await client.send(json.dumps({
                            'stream_id': stream_id,
                            'value': streams[stream_id]
                        }))
            elif data['type'] == 'fetch':
                stream_id = data['stream_id']
                value = streams.get(stream_id, None)
                await websocket.send(json.dumps({
                    'stream_id': stream_id,
                    'value': value
                }))
    except websockets.exceptions.ConnectionClosed as e:
        print(f"Client disconnected: {e}")
    finally:
        connected_clients.remove(websocket)

# Start the WebSocket server with ping_interval=None
async def start_server():
    async with websockets.serve(stream_handler, "localhost", 8765, ping_interval=None):
        print("WebSocket server started on ws://localhost:8765")
        await asyncio.Future()  # Keep the server running

if __name__ == "__main__":
    asyncio.run(start_server())
