import asyncio
# test using async
# Class responsible for updating the value in an infinite loop
class Engine:
    def __init__(self):
        self.value = 0

    async def test_update_value(self, rate):
        while True:
            self.value += 1  # Increment the value
            await asyncio.sleep(rate)  # Sleep for 1 second to simulate work

# Class responsible for printing the value in an infinite loop
class Negotiator:
    def __init__(self, updater):
        self.updater = updater

    async def pub_sub(self, rate):
        while True:
            print(f"Current value: {self.updater.value}")
            await asyncio.sleep(rate)  # Print every 0.5 seconds

# Main function that sets up and runs both loops concurrently using asyncio
async def main():
    updater = Engine()  # Create updater object
    printer = Negotiator(updater)  # Pass updater to the printer

    # Run both tasks (coroutines) concurrently
    await asyncio.gather(
        updater.test_update_value(0.001),
        printer.pub_sub(0.001)
    )

# Run the asyncio event loop
if __name__ == "__main__":
    asyncio.run(main())
