# This file is the main file for the Win_LJM module. It is the entry point for the module and is responsible for starting the module and running the main loop.
import threading
from data_handler_v1 import CSVDataHandler, FolderHandler
import LJM
import time
import json




class Device:
    device = LJM.LMJdevice()
    #single ended
    main_logger = LJM.LMJlogger(['time_elapsed', 'timestamp', 'A0', 'A1', 'Relay_Val', 'VoltageDiff'])
    
    #differential
    #main_logger = LJM.LMJlogger(['time_elapsed', 'timestamp', 'A0', 'A1', 'Relay_Val', 'PresurePSI'])
    data_handler = CSVDataHandler()
    folder_handler = FolderHandler()

    def Test_start_test(self):
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


class Module_Win_LJM:
    #heavy_stuff = HeavyStuffAPI()
    #_this_wont_be_exposed = NotExposedApi()
    lj = None
    reading_thread = None

    def initLMJ(self):

        self.lj = Device()
        self.lj.device.device_connect()
        self.lj.device.device_setup()
        response = {'message': 'Device initialized'}
        return response

    def ToggleRelay(self, value):
        int_value = int(value)
        lj = self.lj
        lj.device.fioState = int_value
        response = {'message': 'Relay toggled to {0}'.format(int_value)}
        return response
    
    
    def StartRead(self):
        lj = self.lj
        self.reading_thread = threading.Thread(target=lj.device.read_loop, args=(lj.main_logger,)).start()
        #read_thread = threading.Thread(target=lj.device.read_loop, args=(lj.main_logger,)).start()
        response = {'message': lj.device.status}
        return response
    
    def CloseDevice(self):
        print("active threads: ", threading.active_count())
        lj = self.lj
        lj.device.device_close()
        del lj
        #lj = None
    
        
        response = {'message': 'Device closed'}
        return response
    
    def createLog(self):
        lj = self.lj
        log = lj.main_logger.log_createdraft()
        log_dict = { log[0][0]: log[1][0], log[0][1]: log[1][1], log[0][2]: log[1][2], log[0][3]: log[1][3], log[0][4]: log[1][4], log[0][5]: log[1][5]}
        log_json = json.dumps(log_dict)  
        #json = { log[0][0]: log[1][0], log[0][1]: log[1][1], log[0][2]: log[1][2], log[0][3]: log[1][3]}
        response = {'message': str(log_json)}
        return response

    def createDF(self, disablelongresponse=False):
        lj = self.lj
        log = lj.main_logger.log_createdraft()
        lj.data_handler.create_df_from_list(log[0], log[1])
        print(lj.data_handler.df)
        DFjson = lj.data_handler.df_to_json()
        if not disablelongresponse:
            response = {'message': str(DFjson)}
        if disablelongresponse:
            response = {'message': "response too long to display, check logs for full response"} 
        return response
    
    def saveDF(self, name):
        lj = self.lj
        #create directory if it doesnt exist

        #this saves latest df
        #this does not auto log the df be sure to call createDF before saving
        lj.folder_handler.create_folder("Logs/")
        lj.data_handler.df_to_csv("Logs/"+name)
        response = {'message': 'CSV saved'}
        return response
    
    def error(self):
        raise Exception('This is a Python exception')


if __name__ == "__main__":  
    pass