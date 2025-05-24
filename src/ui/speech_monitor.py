
from model import Config,NetworkReport
from business import NetworkMonitor

from typing import Literal,Union,Optional,overload,Any
import time
import threading
import pyttsx3 # type: ignore
from pyttsx3.engine import Engine # type: ignore
from pyttsx3.voice import Voice # type: ignore

# typed facade fror pyttsx3 engine
SpeechPropertyName = Literal['rate', 'volume', 'voice', 'pitch','voices']
SpeechPropertyValue = Union[int, float, str]
SpeechSetPropertyValue = Union[int, float, str,list[Voice]]
class SpeechEngine(Engine):
    @overload
    def setProperty(self, name: Literal['rate', 'pitch'], value: int) -> None: ...
    @overload
    def setProperty(self, name: Literal['volume'], value: float) -> None: ...
    @overload
    def setProperty(self, name: Literal['voice'], value: str) -> None: ...
    @overload
    def getProperty(self,name: Literal['voices']) -> list[Voice]: ...
    @overload
    def getProperty(self, name: Literal['rate', 'pitch']) -> int: ...
    @overload
    def getProperty(self, name: Literal['volume']) -> float: ...
    @overload
    def getProperty(self, name: Literal['voice']) -> str: ...
    
    def setProperty(self, name: SpeechPropertyName, value: SpeechPropertyValue) -> None:
        super().setProperty(name, value) # type: ignore
    def say(self, text:str, name:Optional[str]=None)->None: 
        super().say(text,name) # type: ignore
    def runAndWait(self)->None:
        super().runAndWait()
    def getProperty(self,name: SpeechPropertyName) -> Any:
        return super().getProperty(name) #type: ignore
        
#manager to make vocal message on status change
class SpeechMonitor:
    def __init__(self,network_monitor:NetworkMonitor, config:Config):
        self.network_monitor=network_monitor
        self.config=config
        self.engine:SpeechEngine = pyttsx3.init()# type: ignore[assignment]     
        self.engine.setProperty('rate',config.speech_speed)
        self.engine.setProperty('volume',config.speech_volume)
        self.set_voice(self.config.speech_voice) 
        self.previous_statuses:dict[str,bool]={}
        
    def set_voice(self,speech_voice:str)->None:
        # try to set the voice, either by it's name, it's id, or finding a substring in the name or id or in languages
        # typically use the language, or the engine commercial name
        # I have those voice on my French Windows:
        # id=HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_FR-FR_HORTENSE_11.0
        # name=Microsoft Hortense Desktop - French
        # id=HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0
        # name=Microsoft Zira Desktop - English (United States)
        # id=HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_DAVID_11.0
        # name=Microsoft David Desktop - English (United States)
        # gender and age were always None et langueages was empty list
        voices=self.engine.getProperty('voices')
        # search for exact matches
        for voice in voices: #type: ignore
            if speech_voice == voice.id  or speech_voice == voice.name or speech_voice in voice.languages:  # type: ignore
                self.engine.setProperty('voice',voice.id) # type: ignore
                return
        #then search for substring contained
        for voice in voices: #type: ignore
            if speech_voice.lower() in voice.name.lower() or speech_voice.lower() in voice.id.lower() :  # type: ignore
                self.engine.setProperty('voice',voice.id) # type: ignore
                return
        # if not found, list all voices and current voice
        print(f"Cannot set speech voice with '{speech_voice}'")
        for voice in self.engine.getProperty('voices'): #type: ignore
            print(f"Available Voice: '{voice.id}' name='{voice.name}' languages='{voice.languages}' gender='{voice.gender}' age='{voice.age}'") # type: ignore
        voice=self.engine.getProperty('voice')
        print(f"Current voice: {voice}")
   
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
            
            # vocal message only if all devices are tested and if state have changed
            if status_changed and not status_incomplete:
                down_devices =[report.device.name for report in report.devices_down]
                if down_devices:
                    message = f"{' , '.join(down_devices)} {self.config.speech_text_unreachable}"
                else:
                    message = f"{self.config.speech_text_all_is_reachable}"
                self.engine.say(message)
                self.engine.runAndWait()
            elapsed = time.time() - start_time
            if status_incomplete:
                time.sleep(1.0)
            else:
                time.sleep(max(0.0, self.config.interval - elapsed))
            previous_report=report

    def start(self):
        self.speech_monitor_thread = threading.Thread(
            target=self.speech_monitor,
            args=(),
            daemon=True
        )
        self.speech_monitor_thread.start()
