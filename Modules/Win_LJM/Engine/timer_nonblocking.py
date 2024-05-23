#run a function every 200ms non-blocking

import time
import threading

class TimerNonBlocking:
    def __init__(self, interval):
        self.interval = interval
        self.global_timer_runner = True

    def timer_info(self, time_run, run_delayed):
        print("function called at", time_run)
        print("function completed at", time.time())
        print("function delayed by", run_delayed)

    def run_timer(self):
        last_run = time.time()
        while self.global_timer_runner:
            current_time = time.time()
            if current_time - last_run >= self.interval:
                run_delayed = time.time() - last_run - self.interval
                t = threading.Thread(target=self.timer_info, args=(current_time, run_delayed,))
                t.start()
                last_run = time.time()
            else:
                pass

    def start(self):
        threading.Thread(target=self.run_timer).start()

    def stop(self):
        self.global_timer_runner = False


# test the timer
if __name__ == "__main__":
    timer = TimerNonBlocking(0.2)
    timer.start()
    time.sleep(5)
    timer.stop()
    