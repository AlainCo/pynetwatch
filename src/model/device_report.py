from typing import Optional
from model import Device

class DeviceReport:
    def __init__(self,device:Device):
        self.device=device
        self.last_status: Optional[bool] = None
        self.downtime_start: Optional[float] = None  # Type float pour les timestamps
        self.current_status: Optional[bool] = None
