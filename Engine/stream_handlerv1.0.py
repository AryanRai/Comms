from aiohttp import web
import asyncio
import json

# List to keep track of connected WebSocket clients
clients = set()

# WebSocket handler
async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    # Register the client
    clients.add(ws)
    try:
        async for msg in ws:
            if msg.type == web.WSMsgType.TEXT:
                data = json.loads(msg.data)
                if data['type'] == 'update':
                    print(f"Received update: {data}")
                    # Broadcast the update to all connected clients
                    broadcast_data = json.dumps({
                        'type': 'update',
                        'stream_id': data['stream_id'],
                        'value': data['value'],
                        'priority': data['priority']
                    })
                    await broadcast_to_clients(broadcast_data)
                await ws.send_str(json.dumps({'status': 'ok'}))
    finally:
        # Unregister the client
        clients.remove(ws)

    return ws

# Function to broadcast messages to all connected clients
async def broadcast_to_clients(message):
    if clients:  # Check if there are any connected clients
        await asyncio.wait([client.send_str(message) for client in clients])

# Create and run the server
app = web.Application()
app.add_routes([web.get('/', websocket_handler)])

if __name__ == '__main__':
    web.run_app(app, port=8765)


#1.0 server + client pub works at 0.05 + client sub 