# This file is the main file for the Win_LJM module. It is the entry point for the module and is responsible for starting the module and running the main loop.
import threading
from data_handler_v1 import CSVDataHandler, FolderHandler
import LJM
import time


class Win_LMJ:
    device = LJM.LMJdevice()
    main_logger = LJM.LMJlogger(['time_elapsed', 'A0', 'A1', 'Relay_Val'])
    data_handler = CSVDataHandler()
    folder_handler = FolderHandler()

    def start_test(self):
        #labjack
        #device = LJM.LMJdevice()
        #main_logger = LJM.LMJlogger(['time_elapsed', 'A0', 'A1', 'Relay_Val'])
        #t = threading.Thread(target=device.read_loop, args=(main_logger,)).start()
        time.sleep(5)
        self.device.fioState = 1
        time.sleep(5)
        self.device.device_close() #doesnt work need to fix by terminating loop in device
        #print("device closed")

        
        #data handler
        
        #test
        #log_time = [0, 1, 2, 3]
        #A0 = [90, 40, 80, 98]
        #A1 = [90, 40, 80, 98]
        #Relay_Val = [True, False, True, False]
        log = self.main_logger.log_createdraft()
        self.data_handler.create_df_from_list(log[0], log[1])
        self.data_handler.print_df()
        
        

        #data handler


        #test timer
        #timer = timer_nonblocking.TimerNonBlocking(0.2)
        #timer.start()
        #time.sleep(5)
        #timer.stop()


    


if __name__ == "__main__":  
    Win_LMJ()