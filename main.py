#define communication types
import sys
# the mock-0.3.1 dir contains testcase.py, testutils.py & mock.py
import imp
import threading
#engine = imp.load_source("engine","Engine/engine.py")
#gui = imp.load_source("gui","Gui/app.py")
    

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
        CommsLJM = imp.load_source("CommsLJM","Modules/Win_LJM/Engine/CommsLJM.py")
        return CommsLJM
    
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
    engine = threading.Thread(target=imp.load_source("engine","Engine/engine.py"), args=(10,))
    engine.start()
    gui = threading.Thread(target= imp.load_source("gui","Gui/app.py"), args=(10,))
    gui.start()
    gui.join()
    engine.join()
 
    print("Done!")