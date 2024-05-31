#define communication types
import sys
# the mock-0.3.1 dir contains testcase.py, testutils.py & mock.py
import imp
import importlib.util
import random
import threading
import time
import json

import webview
#engine = imp.load_source("engine","Engine/engine.py")
#gui = imp.load_source("gui","Gui/app.py")
    
class HeavyStuffAPI:
    def __init__(self):
        self.cancel_heavy_stuff_flag = False

    def doHeavyStuff(self):
        time.sleep(0.1)  # sleep to prevent from the ui thread from freezing for a moment
        now = time.time()
        self.cancel_heavy_stuff_flag = False
        for i in range(0, 1000000):
            _ = i * random.randint(0, 1000)
            if self.cancel_heavy_stuff_flag:
                response = {'message': 'Operation cancelled'}
                break
        else:
            then = time.time()
            response = {
                'message': 'Operation took {0:.1f} seconds on the thread {1}'.format(
                    (then - now), threading.current_thread()
                )
            }
        return response

    def cancelHeavyStuff(self):
        time.sleep(0.1)
        self.cancel_heavy_stuff_flag = True

class NotExposedApi:
    def notExposedMethod(self):
        return 'This method is not exposed'

class Api:
    heavy_stuff = HeavyStuffAPI()
    _this_wont_be_exposed = NotExposedApi()
    lj = None

    def init(self):
        response = {'message': 'Hello from Python {0}'.format(sys.version)}
        return response


    def initLMJ(self):

        lj = CommunicationHardwawre.Win_LJM().Win_LMJ()
        self.lj = lj
        self.lj.device.device_connect()
        self.lj.device.device_setup()
        response = {'message': 'LMJ initialized'}
        return response

    def ToggleRelay(self, value):
        int_value = int(value)
        lj = self.lj
        lj.device.fioState = int_value
        response = {'message': 'Relay toggled to {0}'.format(int_value)}
        return response
    
    
    def StartRead(self):
        lj = self.lj
        reading_thread = threading.Thread(target=lj.device.read_loop, args=(lj.main_logger,)).start()
        #read_thread = threading.Thread(target=lj.device.read_loop, args=(lj.main_logger,)).start()
        response = {'message': 'Reading started'}
        return response
    
    def CloseDevice(self):
        lj = self.lj
        lj.device.device_close()
        lj = None
        response = {'message': 'Device closed'}
        return response
    
    def createLog(self):
        lj = self.lj
        log = lj.main_logger.log_createdraft()
        log_dict = { log[0][0]: log[1][0], log[0][1]: log[1][1], log[0][2]: log[1][2], log[0][3]: log[1][3]}
        log_json = json.dumps(log_dict)  
        #json = { log[0][0]: log[1][0], log[0][1]: log[1][1], log[0][2]: log[1][2], log[0][3]: log[1][3]}
        response = {'message': str(log_json)}
        return response

    def createDF(self):
        lj = self.lj
        log = lj.main_logger.log_createdraft()
        lj.data_handler.create_df_from_list(log[0], log[1])
        print(lj.data_handler.df)
        DFjson = lj.data_handler.df_to_json()
        response = {'message': DFjson}
        return response
    
    def saveDF(self, name):
        lj = self.lj
        #create directory if it doesnt exist
        lj.folder_handler.create_folder("Logs/")
        lj.data_handler.df_to_csv("Logs/"+name)
        response = {'message': 'CSV saved'}
        return response

    def error(self):
        raise Exception('This is a Python exception')


    
class ProcessHandler:
    def start_engine():
            spec = importlib.util.spec_from_file_location("engine", "Engine/engine.py")
            engine = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(engine)
            return engine


    def start_gui():
            spec = importlib.util.spec_from_file_location("gui", "Gui/app.py")
            gui = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(gui)
            return gui

class CommunicationHardwawre:
    def Win_bluetooth():
        bluetooth = imp.load_source("MAVlink","Modules/Win_bluetooth/Engine/Win_bluetooth.py")
        return bluetooth

    def Win_wifi():
        wifi = imp.load_source("wifi","Modules/Win_wifi/Engine/wifi.py")
        return wifi

    def Win_usb():
        usb = SourceFileLoader("usb","Modules/Win_Mavlink/Engine/usb.py").load_module()
        return usb
    
    def Win_ethernet():
        wifi = SourceFileLoader("wifi","Modules/Win_wifi/Engine/wifi.py").load_module()
        return wifi    
    
    def Win_LJM():
        #CommsLJM = importlib.import_module("Modules/Win_LJM/Engine/main.py")
        sys.path.append("Modules/Win_LJM/Engine/")
        import Win_LMJ
        return Win_LMJ
    
    def Win_LoRa():
        CommsLJM = imp.load_source("CommsLoRa","Modules/Win_LoRa/Engine/CommsLoRa.py")
        return CommsLJM


class CommunicationProtocol:
    def RPi_Mavlink():
        mavlink = SourceFileLoader("CommsMavlink","Modules/RPi_Mavlink/Engine/CommsMavlink.py").load_module()
        #also import gpio communication hardware
        return mavlink
    
    
    def Win_rs485():
        rs485 = SourceFileLoader("rs485","Modules/Win_rs485/Engine/rs485.py").load_module()
        #also import gpio communication hardware
        return rs485

    def Win_ssh():
        ssh = SourceFileLoader("ssh","Modules/ssh/Engine/ssh.py").load_module()
        #also import wifi communication hardware
        return ssh
    
    
if __name__ =="__main__":
    


    
    spec = importlib.util.spec_from_file_location("engine", "Engine/engine.py")
    engine = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(engine)

    
    api = Api()
    window = webview.create_window('Valve Test', "GUI/aresUI/DAQ.html", js_api=api)
    webview.start()


    

    #engine_thread.join()
    

 
    print("Done!")