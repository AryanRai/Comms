#!/usr/bin/env python3
"""
Simple WebSocket connection test for Stream Handler v4.0
Tests if the WebSocket server is properly accepting connections
"""

import asyncio
import websockets
import json
import time

async def test_websocket_connection():
    """Test WebSocket connection to Stream Handler"""
    try:
        print("Testing WebSocket connection to ws://localhost:3000...")
        
        # Connect to the WebSocket server
        async with websockets.connect("ws://localhost:3000") as websocket:
            print("✅ WebSocket connection established!")
            
            # Send a test message
            test_message = {
                "type": "ping",
                "source": "test_client",
                "timestamp": time.time(),
                "target": "sh",
                "msg-sent-timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            print(f"Sending test message: {test_message}")
            await websocket.send(json.dumps(test_message))
            
            # Wait for response
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"✅ Received response: {response}")
                
                # Parse response
                response_data = json.loads(response)
                if response_data.get('type') == 'pong':
                    print("✅ Ping-pong test successful!")
                else:
                    print(f"📨 Received message type: {response_data.get('type')}")
                
            except asyncio.TimeoutError:
                print("⚠️ No response received within 5 seconds")
                
    except ConnectionRefusedError:
        print("❌ Connection refused - Stream Handler not running on port 3000")
    except Exception as e:
        print(f"❌ Connection error: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket_connection())