from aiohttp import web
import asyncio
import json

# Create WebSocket handler
async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    async for msg in ws:
        if msg.type == web.WSMsgType.TEXT:
            data = json.loads(msg.data)
            if data['type'] == 'update':
                print(f"Received update: {data}")
            await ws.send_str(json.dumps({'status': 'ok'}))

    return ws

# Create and run the server
app = web.Application()
app.add_routes([web.get('/', websocket_handler)])

if __name__ == '__main__':
    web.run_app(app, port=8765)
