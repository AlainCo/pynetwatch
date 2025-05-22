from __future__ import annotations
from model import DeviceReport

class NetworkReport:
    def __init__(self):
        self.devices_up:list[DeviceReport]=[]
        self.devices_down:list[DeviceReport]=[]
        self.devices_unknown:list[DeviceReport]=[]
        self.devices_down_important:list[DeviceReport]=[]
        
    def changed_from(self,previous:NetworkReport) -> bool:
        up1=set(d.device.name for d in self.devices_up)
        up0=set(d.device.name for d in previous.devices_up)
        diff=up0^up1
        return bool(diff)
     
    
    