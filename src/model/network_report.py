from model import DeviceReport

class NetworkReport:
    def __init__(self):
        self.devices_up:set[DeviceReport]=set()
        self.devices_down:set[DeviceReport]=set()
        self.devices_unknown:set[DeviceReport]=set()
        self.devices_down_important:set[DeviceReport]=set()
        
    
    