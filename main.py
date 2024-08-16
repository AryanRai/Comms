#define communication types
import sys
# the mock-0.3.1 dir contains testcase.py, testutils.py & mock.py

import importlib.util
import random
import threading
import time
import json
import webview
import data_handler

'''
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
'''

    
class engine:
    Module_list = {}
    
    def load_module(self, module):
        #todo: check if module is valid and add it if folder exists
        if module in self.Module_list:
            sys.path.append("Modules/"+module+"/Engine/")
            self.Module_list[module] = importlib.import_module(module)
            
        
        #first check if folder exists
        #second add to sys path
        #import python module
        #import gui
        #add to module list
        
      
    def __init__(self):
        Modules = data_handler.FolderHandler().list_subfolders("Modules/")
        for module in Modules:
            self.Module_list[module] = "Not Loaded"

        #todo: impelment dynamic module loading later on
        
        
        for module in self.Module_list:
            self.load_module(module)
            print(self.Module_list)
    


    
class Api:
    engine = None
    Module_Labjack = None
    #Module_Labjack = Module_Win_LJM(engine)

    def __init__(self, engine):
        self.engine = engine
        self.Module_Labjack = engine.Module_list["Win_LJM"].Module_Win_LJM()
        print(self.Module_Labjack)
            

    '''

class CommunicationProtocol:
    def RPi_Mavlink():
        mavlink = SourceFileLoader("CommsMavlink","Modules/RPi_Mavlink/Engine/CommsMavlink.py").load_module()
        #also import gpio communication hardware
        return mavlink
    
    
    def Win_rs485():
        rs485 = SourceFileLoader("rs485","Modules/Win_rs485/Engine/rs485.py").load_module()
        #also import gpio communication hardware
        return rs485

'''

    
if __name__ =="__main__":

    engine = engine()
    api = Api(engine)
    window = webview.create_window('Valve Test', "GUI/aresUI/DAQ.html", js_api=api, width=1000, height=600, resizable=True, background_color='#000000', text_select=True)
    webview.start()
    

 
    print("Done!")