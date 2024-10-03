import threading
import time

# Class responsible for updating the value in an infinite loop
class ValueUpdater:
    def __init__(self):
        self.value = 0

    def update_value(self, rate):
        while True:
            self.value += 1  # Increment the value
            time.sleep(rate)    # Sleep for 1 second to simulate work

# Class responsible for printing the value in an infinite loop
class ValuePrinter:
    def __init__(self, updater):
        self.updater = updater

    def print_value(self, rate):
        while True:
            print(f"Current value: {self.updater.value}")
            time.sleep(rate)  # Print every 0.5 seconds

# Main function that sets up and runs both loops concurrently
def main():
    # Create the updater object
    updater = ValueUpdater()

    # Create the printer object, sharing the updater instance
    printer = ValuePrinter(updater)

    # Create two threads: one for updating the value, one for printing it
    update_thread = threading.Thread(target=updater.update_value, args=(0.001,))
    print_thread = threading.Thread(target=printer.print_value, args=(0.001,))

    # Start both threads
    update_thread.start()
    print_thread.start()

    # Join threads to keep the main function running (optional in this case)
    update_thread.join()
    print_thread.join()

# Run the main function
if __name__ == "__main__":
    main()
