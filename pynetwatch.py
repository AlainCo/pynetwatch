from typing import Optional,Literal, Union, overload,Any
import requests
import time
import threading
import queue
from queue import Queue
import json
from pathlib import Path
import tkinter as tk
from tkinter import ttk
import pyttsx3 # type: ignore
from pyttsx3.engine import Engine # type: ignore
from icmplib import ping as icmp_ping # type: ignore





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
        super().setProperty(name, value) # type: ignore[assignment]
    def say(self, text:str, name:Optional[str]=None)->None: 
        super().say(text,name) # type: ignore[assignment]
    def runAndWait(self)->None:
        super().runAndWait()
        
class Config:
    def __init__(self):
        # Valeurs par défaut
        self.speech_speed = 140
        self.speech_volume=1.0
        self.interval = 10
        self.ping_count = 2
        self.ping_timeout = 1
        self.http_timeout = 3
        self.http_retry = 2
        self.update_interval=1000

        
    def load_config_from_json(self, filename: str = "config.json") -> None:
        """Charge les données du JSON dans les attributs de la classe."""
        file_path = Path(filename)
        
        # Crée le fichier JSON avec les valeurs par défaut s'il n'existe pas
        if not file_path.exists():
            self._generate_default_config(file_path)
        
        # Charge et applique les données du JSON
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for key, value in data.items():
                if hasattr(self, key):  # Ne met à jour que les attributs existants
                    setattr(self, key, value)
    
    def _generate_default_config(self, path: Path) -> None:
        """Génère un fichier JSON avec les valeurs par défaut de la classe."""
        with open(path, 'w', encoding='utf-8') as f:
            # Convertit les attributs de la classe en dictionnaire, excluant les méthodes
            default_data = {k: v for k, v in self.__dict__.items() if not k.startswith('_')}
            json.dump(default_data, f, indent=4)


class Device:
    def __init__(
        self,
        name: str,
        ip: Optional[str] = None,
        url: Optional[str] = None,
        is_important: bool = False
    ):
        self.name: str = name
        self.ip: Optional[str] = ip
        self.url: Optional[str] = url
        self.is_important: bool = is_important
        

class DeviceMonitor:
    def __init__(self, device: Device):
        self.device: Device = device
        self.last_status: Optional[bool] = None
        self.downtime_start: Optional[float] = None  # Type float pour les timestamps
        self.current_status: Optional[bool] = True

class AlertData:
    def __init__(self,kind:str,device:Device,status:bool,time:float):
        self.kind=kind
        self.device=device.name
        self.status=status
        self.time=time

class NetworkMonitorApp(tk.Tk):
    def __init__(self, device_monitors:dict[str,DeviceMonitor], alert_queue:Queue[AlertData], config:Config, *args:Any, **kwargs:Any):
        super().__init__(*args, **kwargs)
        self.title("Network Monitor")
        self.alert_queue = alert_queue
        self.device_monitors = device_monitors
        
        # Configuration de l'interface
        self.tree = ttk.Treeview(self, columns=('Status', 'Downtime'), show='headings')
        self.tree.heading('Status', text='Statut')
        self.tree.heading('Downtime', text='Indisponible depuis')
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        self.status_label = ttk.Label(self, text="Initialisation", foreground="green")
        self.status_label.pack()
        
        self.update_interval = config.update_interval
        self.update_display()
    
    def update_display(self):
        try:
            alert_data = self.alert_queue.get_nowait()
            self.process_alert(alert_data)
        except queue.Empty:
            pass
        
        self.tree.delete(*self.tree.get_children())
        any_down = False
        
        for monitor in self.device_monitors.values():
            if monitor.current_status is False:
                any_down = True
                downtime = time.strftime("%H:%M:%S", time.localtime(monitor.downtime_start)) if monitor.downtime_start else "N/A"
                self.tree.insert('', 'end', values=(monitor.device.name, downtime))
        
        if any_down:
            self.status_label.config(text="Problèmes détectés", foreground="red")
        else:
            self.status_label.config(text="Tout est joignable", foreground="green")
        
        self.after(self.update_interval, self.update_display)
    
    def process_alert(self, alert_data:AlertData):
        if alert_data.kind == "status_change":
            device_name:str = alert_data.device
            monitor = self.device_monitors[device_name]
            if not alert_data.status:
                monitor.downtime_start = time.time()
            else:
                monitor.downtime_start = None

def check_ping(host:str, count:int=1, timeout:int=1):
    try:
        result = icmp_ping(host, count=count, timeout=timeout, privileged=False)
        return result.packets_received > 0
    except Exception:
        return False

def check_url(url:str, retry:int=1,timeout:int=5):
    i=0
    while i<retry:
        try:
            response = requests.get(url, timeout=timeout, verify=False)
            return response.status_code <500
        except requests.exceptions.RequestException:
            i += 1
    else:
        return False

def monitor(device_monitors:dict[str,DeviceMonitor], alert_queue:Queue[AlertData], config:Config):
    engine:SpeechEngine = pyttsx3.init()# type: ignore[assignment]
    engine.setProperty('rate',config.speech_speed)
    engine.setProperty('volume',config.speech_volume)
    engine.setProperty('voice', 'french') 
    
    while True:
        start_time:float = time.time()
        status_changes:list[Device] = []
        
        for monitor in device_monitors.values():
            previous_status = monitor.current_status
            device=monitor.device;
            # Vérification du statut
            ok:bool = False
            if device.ip:
                ok = check_ping(device.ip, config.ping_count, config.ping_timeout)
            if not ok and device.url:
                ok = check_url(device.url, config.http_retry, config.http_timeout)
            
            monitor.current_status = ok
            
            # Détection des changements d'état
            if previous_status != ok:
                if ok:
                    downtime_duration = time.time() - monitor.downtime_start if monitor.downtime_start else 0
                    print(f"[{time.strftime('%H:%M:%S')}] {device.name} reconnecté (indisponible pendant {downtime_duration:.1f}s)")
                else:
                    monitor.downtime_start = time.time()
                    print(f"[{time.strftime('%H:%M:%S')}] {device.name} injoignable")
                
                alert_queue.put( AlertData(kind="status_change",device=device,status=ok,time=time.time()))
                status_changes.append(device)
        
        # Message vocal uniquement si changement
        if status_changes:
            down_devices = [d.name for d in devices if not device_monitors[d.name].current_status]
            if down_devices:
                message = f"{' '.join(down_devices)} injoignable"
            else:
                message = "Tout est joignable"
            
            engine.say(message)
            engine.runAndWait()
        
        elapsed = time.time() - start_time
        time.sleep(max(0, config.interval - elapsed))

def load_devices_from_json(filename:str="devices.json")->list[Device]:
    devices:list[Device] = []
    try:
        file_path = Path(filename)
        if not file_path.exists():
            raise FileNotFoundError(f"Fichier {filename} introuvable")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        for item in data:
            if 'name' not in item:
                print(f"Erreur: Entrée invalide dans le JSON - clé 'name' manquante: {item}")
                continue
                
            devices.append(Device(
                name=item['name'],
                ip=item.get('ip'),
                url=item.get('url'),
                is_important=item.get('is_important', False)
            ))
            
        return devices
    
    except json.JSONDecodeError as e:
        print(f"Erreur de parsing JSON: {e}")
        return []
    except Exception as e:
        print(f"Erreur de chargement: {str(e)}")
        return []



if __name__ == "__main__":
    config:Config=Config()
    config.load_config_from_json("config.json")

    # Charger les périphériques depuis le fichier JSON
    devices = load_devices_from_json()
    
    if not devices:
        print("Aucun périphérique chargé. Vérifiez le fichier devices.json")
        exit(1)
    
    alert_queue:Queue[AlertData] = queue.Queue()
    device_monitors:dict[str,DeviceMonitor] = {device.name: DeviceMonitor(device) for device in devices}
    
    # Démarrer le thread de monitoring
    monitor_thread = threading.Thread(
        target=monitor,
        args=(device_monitors, alert_queue, config),
        daemon=True
    )
    monitor_thread.start()
    
    # Lancer l'interface graphique
    app = NetworkMonitorApp(device_monitors, alert_queue,config)
    app.mainloop()