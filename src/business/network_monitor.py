
import threading
from threading import Thread
import urllib3 
from model import Config,Device
from business import DeviceMonitor

# gestionnaire des thread de surveillances réseaux
class NetworkMonitor:
    def __init__(self,devices:list[Device], config:Config):
        self.config=config
        self.device_monitors=[DeviceMonitor(device) for device in devices]
        urllib3.disable_warnings()
        
    def start(self):
        self.monitors_threads:list[Thread]=[
                threading.Thread(
                    target=monitor.run_monitor,
                    args=(self.config,),
                    daemon=True) 
                for monitor in self.device_monitors 
        ]
        for thread in self.monitors_threads:
            thread.start()

