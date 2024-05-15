#define communication types
from importlib.machinery import SourceFileLoader

class CommunicationType:
    def Win_bluetooth():
        bluetooth = SourceFileLoader("MAVlink","Modules/Win_bluetooth/Engine/Win_bluetooth.py").load_module()
        return bluetooth

    def Win_wifi():
        wifi = SourceFileLoader("wifi","Modules/Win_wifi/Engine/wifi.py").load_module()
        return wifi

    def Win_usb():
        usb = SourceFileLoader("usb","Modules/Win_Mavlink/Engine/usb.py").load_module()
        return usb
    


class CommunicationProtocol:
    def RPi_Mavlink():
        mavlink = SourceFileLoader("MAVlink","Modules/RPi_Mavlink/Engine/Mavlink.py").load_module()
        return mavlink
    
    
    def Win_rs485():
        rs485 = SourceFileLoader("rs485","Modules/Win_rs485/Engine/rs485.py").load_module()
        return rs485

    def ssh():
        ssh = SourceFileLoader("ssh","Modules/ssh/Engine/ssh.py").load_module()
        return ssh
    
