# This file is the main file for the Win_LJM module. It is the entry point for the module and is responsible for starting the module and running the main loop.
import threading
from data_handler_v1 import CSVDataHandler
import LJM
import time


def main():
    #labjack
    device = LJM.LMJdevice()
    main_logger = LJM.LMJlogger(['time_elapsed', 'A0', 'A1', 'Relay_Val'])
    t = threading.Thread(target=device.read_loop, args=(main_logger,)).start()
    time.sleep(5)
    device.device_close() #doesnt work need to fix by terminating loop in device
    print("device closed")

    
    #data handler
    data_handler = CSVDataHandler()
    #test
    #log_time = [0, 1, 2, 3]
    #A0 = [90, 40, 80, 98]
    #A1 = [90, 40, 80, 98]
    #Relay_Val = [True, False, True, False]
    log = main_logger.log_createdraft()
    data_handler.create_df_from_list(log[0], log[1])
    data_handler.print_df()
    

    #data handler


    #test timer
    #timer = timer_nonblocking.TimerNonBlocking(0.2)
    #timer.start()
    #time.sleep(5)
    #timer.stop()


    


if __name__ == "__main__":  
    main()