
#stream_handler.py v0.1 only supports up to 0.1 not 0.001 or 0.01
#this is the first version which uses priority queue to process streams
#only for testing   

import asyncio
import websockets
import json
from collections import defaultdict, deque
import heapq

# Priority levels
HIGH_PRIORITY = 1
LOW_PRIORITY = 2

# Priority queue for streams
priority_queue = []
stream_data = defaultdict(lambda: {'priority': LOW_PRIORITY, 'value': None})
streams_lock = asyncio.Lock()

async def process_high_priority_streams():
    while True:
        await asyncio.sleep(0.001)  # Adjust frequency as needed
        async with streams_lock:
            while priority_queue:
                priority, stream_id = heapq.heappop(priority_queue)
                if stream_data[stream_id]['priority'] == HIGH_PRIORITY:
                    # Process high-priority streams
                    value = stream_data[stream_id]['value']
                    print(f"Processing high-priority stream {stream_id} with value: {value}")
                    # Optionally, broadcast to clients
                    # ...

async def process_low_priority_streams():
    while True:
        await asyncio.sleep(0.01)  # Adjust frequency as needed
        async with streams_lock:
            for stream_id, data in stream_data.items():
                if data['priority'] == LOW_PRIORITY:
                    # Process low-priority streams
                    value = data['value']
                    print(f"Processing low-priority stream {stream_id} with value: {value}")
                    # Optionally, broadcast to clients
                    # ...

async def stream_handler(websocket, path):
    async for message in websocket:
        data = json.loads(message)
        async with streams_lock:
            stream_id = data['stream_id']
            if data['type'] == 'update':
                # Update the stream data and priority
                stream_data[stream_id]['value'] = data['value']
                stream_data[stream_id]['priority'] = data.get('priority', LOW_PRIORITY)

                # Add to priority queue if high priority
                if stream_data[stream_id]['priority'] == HIGH_PRIORITY:
                    heapq.heappush(priority_queue, (HIGH_PRIORITY, stream_id))
                else:
                    # Handle low priority streams differently if needed
                    pass

                print(f"Updated stream {stream_id} with value: {data['value']}")

                # Optionally, send a confirmation back to the sender
                await websocket.send(json.dumps({
                    'status': 'ok',
                    'stream_id': stream_id,
                    'value': stream_data[stream_id]['value']
                }))
            elif data['type'] == 'fetch':
                value = stream_data.get(stream_id, {}).get('value', None)
                await websocket.send(json.dumps({
                    'stream_id': stream_id,
                    'value': value
                }))

async def start_server():
    server = await websockets.serve(stream_handler, "localhost", 8765, ping_interval=None, max_size=2**25)
    print("WebSocket server started on ws://localhost:8765")
    await asyncio.gather(
        process_high_priority_streams(),
        process_low_priority_streams(),
        server.wait_closed()
    )

if __name__ == "__main__":
    asyncio.run(start_server())


