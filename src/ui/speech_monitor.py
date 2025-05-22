
from model import Config
from business import DeviceMonitor

from typing import Literal,Union,Optional,overload
import time
import threading
import pyttsx3 # type: ignore
from pyttsx3.engine import Engine # type: ignore

# facade typée de la synthèse vocale
SpeechPropertyName = Literal['rate', 'volume', 'voice', 'pitch']
SpeechPropertyValue = Union[int, float, str]
class SpeechEngine(Engine):
    @overload
    def setProperty(self, name: Literal['rate', 'pitch'], value: int) -> None: ...
    @overload
    def setProperty(self, name: Literal['volume'], value: float) -> None: ...
    @overload
    def setProperty(self, name: Literal['voice'], value: str) -> None: ...
    
    def setProperty(self, name: SpeechPropertyName, value: SpeechPropertyValue) -> None:
        super().setProperty(name, value) # type: ignore
    def say(self, text:str, name:Optional[str]=None)->None: 
        super().say(text,name) # type: ignore
    def runAndWait(self)->None:
        super().runAndWait()
        
#gestionnaire de l'interface vocale de la surveillance
class SpeechMonitor:
    def __init__(self,device_monitors:list[DeviceMonitor], config:Config):
        self.device_monitors=device_monitors
        self.config=config
        self.engine:SpeechEngine = pyttsx3.init()# type: ignore[assignment]
        self.engine.setProperty('rate',config.speech_speed)
        self.engine.setProperty('volume',config.speech_volume)
        self.engine.setProperty('voice', 'french') 
        self.previous_statuses:dict[str,bool]={}
   
    def speech_monitor(self):
        status_incomplete=True
        while True:
            start_time:float = time.time()
            status_changed=status_incomplete
            status_incomplete=False
            for monitor in self.device_monitors:
                name=monitor.device.name
                current_status=monitor.current_status
                if current_status is not None:
                    if  name in self.previous_statuses:
                        if not current_status==self.previous_statuses[name]: 
                            status_changed=True
                    self.previous_statuses[name]=current_status
                else:
                    status_incomplete=True
            # Message vocal uniquement si changement
            if status_changed and not status_incomplete:
                down_devices = [m.device.name for m in self.device_monitors if m.current_status==False]
                if down_devices:
                    message = f"{' , '.join(down_devices)} injoignable"
                else:
                    message = "Tout est joignable"
                self.engine.say(message)
                self.engine.runAndWait()
            elapsed = time.time() - start_time
            time.sleep(max(0.0, self.config.interval - elapsed))

    def start(self):
         # Démarrer le thread de speech monitoring
        self.speech_monitor_thread = threading.Thread(
            target=self.speech_monitor,
            args=(),
            daemon=True
        )
        self.speech_monitor_thread.start()
