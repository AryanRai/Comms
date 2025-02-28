#write a code to run a function every 200ms and the exact time of the function call since the start of the program
import time
def function():
    print("function called at",time.time())
    time.sleep(1)
def timer(func, interval):
    start = time.time()
    while True:
        func()
        time.sleep(interval - ((time.time() - start) % interval))

timer(function, 0.2)
# """
# # Close interval and device handles