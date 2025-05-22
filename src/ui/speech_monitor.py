
from model import Config,NetworkReport
from business import NetworkMonitor

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
    def __init__(self,network_monitor:NetworkMonitor, config:Config):
        self.network_monitor=network_monitor
        self.config=config
        self.engine:SpeechEngine = pyttsx3.init()# type: ignore[assignment]
        self.engine.setProperty('rate',config.speech_speed)
        self.engine.setProperty('volume',config.speech_volume)
        self.engine.setProperty('voice', 'french') 
        self.previous_statuses:dict[str,bool]={}
   
    def speech_monitor(self):

        previous_report=NetworkReport()
        while True:
            start_time:float = time.time()
            report=self.network_monitor.get_report()
            if previous_report.devices_unknown:
                status_changed=True
            else:
                status_changed=report.changed_from(previous_report)
            status_incomplete=report.devices_unknown
            
            # Message vocal uniquement si changement
            if status_changed and not status_incomplete:
                down_devices =[report.device.name for report in report.devices_down]
                if down_devices:
                    message = f"{' , '.join(down_devices)} injoignable"
                else:
                    message = "Tout est joignable"
                self.engine.say(message)
                self.engine.runAndWait()
            elapsed = time.time() - start_time
            if status_incomplete:
                time.sleep(1.0)
            else:
                time.sleep(max(0.0, self.config.interval - elapsed))
            previous_report=report

    def start(self):
         # Démarrer le thread de speech monitoring
        self.speech_monitor_thread = threading.Thread(
            target=self.speech_monitor,
            args=(),
            daemon=True
        )
        self.speech_monitor_thread.start()
