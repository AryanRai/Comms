import asyncio
import websockets
import json
import time

async def publish(rate=0.01):  # rate is the delay between updates
    uri = "ws://localhost:8765"
    
    # Store the number of messages sent
    messages_sent = 0
    
    # Time markers
    start_time = time.time()

    async with websockets.connect(uri, ping_interval=None) as websocket:
        try:
            while True:
                # Create the JSON message
                data = json.dumps({
                    'type': 'update',
                    'stream_id': 'test_stream',
                    'value': messages_sent,
                    'priority': 1
                })
                
                # Send the message
                await websocket.send(data)
                print(f"Sent message {messages_sent}: {data}")

                # Wait for a response (optional)
                response = await websocket.recv()
                print(f"Received: {response}")

                # Increment message counter
                messages_sent += 1

                # Sleep based on the rate (in seconds) between messages
                await asyncio.sleep(rate)
                
                # Optionally, stop after a certain number of messages to avoid infinite loops during testing
                #if messages_sent >= 1000:  # Stop after 1000 messages
                   # break

        except Exception as e:
            print(f"Error: {e}")
        finally:
            # End time and message count
            end_time = time.time()
            print(f"Total Messages Sent: {messages_sent}")
            print(f"Elapsed Time: {end_time - start_time} seconds")


if __name__ == "__main__":
    # Adjust the rate here for testing different frequencies
    rate_to_test = 0.05  # Change this to test different rates like 0.1, 0.01, 0.001, etc.
    asyncio.run(publish(rate_to_test))

#1.0 server + client pub works at 0.05 + client sub 