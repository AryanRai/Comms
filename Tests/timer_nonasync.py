#run a function every 200ms non-blocking

import time
import threading

global_timer_runner = True

def timer_info(time_run, run_delayed):
    print("function called at",time_run)
    print("function completed at",time.time())
    print("function delayed by",run_delayed)


def run_timer(interval):
    last_run = time.time()
    while global_timer_runner == True:
        current_time = time.time()
        if current_time - last_run >= interval:
            run_delayed = time.time() - last_run - interval
            t = threading.Thread(target=timer_info, args=(current_time, run_delayed,))
            t.start()
            
            last_run = time.time()
            
        else:
            pass
            


#test the timer
threading.Thread(target=run_timer, args=(0.2,)).start()

time.sleep(10)
global_timer_runner = False
    