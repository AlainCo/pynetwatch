from typing import Optional,Literal, Union, overload,Any,TextIO
import requests
import urllib3 
import time
import threading
import queue
import sys
import os
from queue import Queue
import json
from pathlib import Path
import tkinter as tk
from tkinter import ttk,Text
import pyttsx3 # type: ignore
from pyttsx3.engine import Engine # type: ignore
from icmplib import ping as icmp_ping # type: ignore

MAX_QUEUE_SIZE = 1000  # Évite l'explosion mémoire

# pour les ressources pyinstaller
def resource_path(relative_path):# type: ignore
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)# type: ignore
    return os.path.join(os.path.abspath("."), relative_path)# type: ignore


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
        self.log_file='nul:'
        self.devices_file='devices.json'
        self.config_file='pynetwatch-config.json'
        self.config_create=False;

        
    def load_config_from_json(self, filename:str) -> None:
        """Charge les données du JSON dans les attributs de la classe."""
        file_path = Path(filename)
        
        # Crée le fichier JSON avec les valeurs par défaut s'il n'existe pas
        if not file_path.exists():
            if self.config_create:
                self._generate_default_config(file_path)
            else:
                exit(2)
        
        # Charge et applique les données du JSON
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for key, value in data.items():
                if hasattr(self, key):  # Ne met à jour que les attributs existants
                    setattr(self, key, value)
       

    def _generate_default_config(self, file_path: Path) -> None:
        """Crée un fichier de configuration par défaut."""
        default_data = {key: getattr(self, key) for key in vars(self)}
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(default_data, f, indent=4)
                
    def load_config_from_cli_args(self, args: list[str] = sys.argv[1:]) -> None:
        """Modifie la configuration avec les arguments de ligne de commande."""
        for arg in args:
            if self._is_valid_arg(arg):
                key, value = self._parse_arg(arg)
                self._set_config_value(key, value)

    def _is_valid_arg(self, arg: str) -> bool:
        """Valide le format des arguments."""
        return arg.startswith('--') and '=' in arg and len(arg.split('=')) == 2

    def _parse_arg(self, arg: str) -> tuple[str, str]:
        """Extrait la clé et la valeur d'un argument."""
        key_value = arg[2:].split('=', 1)
        return key_value[0].strip().replace('-', '_'), key_value[1].strip()

    def _set_config_value(self, key: str, str_value: str) -> None:
        """Convertit et assigne la valeur en respectant le type d'origine."""
        if hasattr(self, key):
            original_value = getattr(self, key)
            target_type:type = type(original_value) # type: ignore
            
            try:
                converted_value = self._convert_value(str_value, target_type)
                setattr(self, key, converted_value)
                print(f"Config: {key} modifié à {converted_value} ({target_type.__name__})")
            except (ValueError, TypeError) as e:
                print(f"Erreur de conversion pour {key}: {str(e)}")
        else:
            print(f"Avertissement: Clé de configuration inconnue - {key}")

    def _convert_value(self, value: str, target_type: type) -> Any:
        """Gère les conversions de type complexes."""
        if target_type == bool:
            return self._convert_to_bool(value)
        try:
            return target_type(value)
        except ValueError:
            # Gestion spéciale pour les float représentés comme int
            if target_type == float and '.' not in value:
                return float(value)
            raise ValueError(f"Impossible de convertir '{value}' en {target_type.__name__}")

    def _convert_to_bool(self, value: str) -> bool:
        """Convertit différentes représentations textuelles en booléen."""
        true_values = ['true', '1', 'yes', 'on', 't', 'y']
        false_values = ['false', '0', 'no', 'off', 'f', 'n']
        lower_val = value.lower()
        
        if lower_val in true_values:
            return True
        if lower_val in false_values:
            return False
        raise ValueError(f"Valeur booléenne non reconnue: {value}")


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
        self.current_status: Optional[bool] = None

class AlertData:
    def __init__(self,kind:str,device:Device,status:bool,time:float):
        self.kind=kind
        self.device=device.name
        self.status=status
        self.time=time


class NetworkMonitorApp(tk.Tk):
    def __init__(self, device_monitors:dict[str,DeviceMonitor], alert_queue:Queue[AlertData], config:Config, *args:Any, **kwargs:Any):
        super().__init__(*args, **kwargs)
        
        # Configuration initiale icones
        self.current_icon = ""
        self.icons = {
            "ok": self._get_icon_path("ok.ico"),
            "warn": self._get_icon_path("warn.ico"),
            "alert": self._get_icon_path("alert.ico")
        }
        
        # Définir l'icône initiale
        self._change_icon(self.current_icon)
        
        
        
        
        self.alert_queue = alert_queue
        self.device_monitors = device_monitors
        # Queue thread-safe pour les logs
        self.log_queue:Queue[str] = queue.Queue()
        
        # Configuration de l'interface
        self.title("Network Monitor")
        self.status_label = ttk.Label(self, text="Initialisation", foreground="green")
        self.status_label.pack(side=tk.TOP)
        
        self.tree = ttk.Treeview(self, columns=('Status', 'Downtime'), show='headings')
        self.tree.heading('Status', text='Statut')
        self.tree.heading('Downtime', text='Indisponible depuis')
        self.tree.pack(fill=tk.BOTH, expand=True)
        

 
        # zone de logs
        self.log_frame = ttk.Frame(self)
        self.log_text = tk.Text(self.log_frame, height=10, state='disabled',width=40)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Bouton pour escamoter
        self.toggle_btn = ttk.Button(
            self,
            text="▲ Afficher les logs ▼",
            command=self.toggle_logs
        )
        self.toggle_btn.pack(fill=tk.X,side=tk.BOTTOM)
        
        self.log_visible = False
        self.log_frame.pack_forget()
        
        # Redirection vers la zone de logs
        sys.stdout = self.LogProducer(sys.stdout, self.log_queue)
        sys.stderr = self.LogProducer(sys.stderr, self.log_queue)
        
        #self.update_interval = config.update_interval
        self.update_interval=1000
        self.update_display()
        #self.after(100, self.process_log_queue)
    
    def toggle_logs(self):
        if self.log_visible:
            self.log_frame.pack_forget()
            self.toggle_btn.config(text="▲ Afficher les logs ▼")
        else:
            self.log_frame.pack(fill=tk.BOTH, expand=True)
            self.toggle_btn.config(text="▲ Masquer les logs ▼")
        self.log_visible = not self.log_visible        
    class LogProducer:
        def __init__(self, original_stream:TextIO, log_queue:Queue[str]):
            self.original_stream = original_stream
            self.log_queue = log_queue
            
        def write(self, message:str):
            self.original_stream.write(message)
            if message.strip():
                if self.log_queue.qsize() < MAX_QUEUE_SIZE:
                    self.log_queue.put(message.strip())
                else:
                    pass
        def flush(self):
            pass

    def process_log_queue(self):
        """Vide la queue de logs dans le widget (thread principal)"""
        while True:
            try:
                msg = self.log_queue.get_nowait()
                self.log_text.configure(state='normal')
                self.log_text.insert('end', msg + '\n')
                self.log_text.see('end')
                self.log_text.configure(state='disabled')
            except queue.Empty:
                break
        #self.after(100, self.process_log_queue)  # Reprogrammation
 
            
    def _get_icon_path(self, filename:str):
        """Gère le chemin des ressources pour PyInstaller"""
        if getattr(sys, 'frozen', False):
            return os.path.join(sys._MEIPASS, "icons", filename) # type: ignore
        return os.path.join("icons", filename)

    def _change_icon(self, icon_name:str):
        """Change l'icône de la fenêtre et de la barre des tâches"""
        if icon_name not in self.icons:
            return
               
        self.current_icon = icon_name
        icon_path = self.icons[icon_name]
        
        # Pour Windows
        if sys.platform == "win32":
            import win32gui
            import win32con
            
            hwnd = win32gui.GetParent(self.winfo_id())
            win32gui.SendMessage(
                hwnd,
                win32con.WM_SETICON,
                win32con.ICON_BIG,
                win32gui.LoadImage(0, icon_path, win32con.IMAGE_ICON, 0, 0, win32con.LR_LOADFROMFILE) #type: ignore
            )
    
    def update_display(self):
        
        self.tree.delete(*self.tree.get_children())
        any_down = False
        important_down=False
        
        for monitor in self.device_monitors.values():
            if monitor.current_status is False:
                any_down = True
                if monitor.device.is_important:
                    important_down=True
                downtime = time.strftime("%H:%M:%S", time.localtime(monitor.downtime_start)) if monitor.downtime_start else "N/A"
                self.tree.insert('', 'end', values=(monitor.device.name, downtime))
        
        
        if important_down:
            self.status_label.config(text="Problèmes graves détectés", foreground="red",font=('Helvetica', 18, 'bold'))
            self._change_icon('alert')
        else:
            if any_down:
                self.status_label.config(text="Problèmes détectés", foreground="orange",font=('Helvetica', 15, 'bold'))
                self._change_icon('warn')
            else:
                self.status_label.config(text="Tout est joignable", foreground="green",font=('Helvetica', 10, 'normal'))
                self._change_icon('ok')
        self.process_log_queue()
        self.after(self.update_interval, self.update_display)
    




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
            response = requests.get(url, timeout=timeout, verify=False,)
            return response.status_code <500
        except requests.exceptions.RequestException as e:
            #print(f"Erreur HTTP pour {url} : {e}")
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
            if previous_status is None or previous_status != ok:
                if ok:
                    downtime_duration = time.time() - monitor.downtime_start if monitor.downtime_start else 0
                    if downtime_duration>0:
                        print(f"[{time.strftime('%H:%M:%S')}] {device.name} reconnecté (indisponible pendant {downtime_duration:.1f}s)")
                    else:
                        print(f"[{time.strftime('%H:%M:%S')}] {device.name} connecté")
                    monitor.downtime_start = None
                else:
                    monitor.downtime_start = time.time()
                    print(f"[{time.strftime('%H:%M:%S')}] {device.name} injoignable")
                
                alert_queue.put( AlertData(kind="status_change",device=device,status=ok,time=time.time()))
                status_changes.append(device)
        
        # Message vocal uniquement si changement
        if status_changes:
            down_devices = [d.name for d in devices if not device_monitors[d.name].current_status]
            if down_devices:
                message = f"{' , '.join(down_devices)} injoignable"
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
    urllib3.disable_warnings()
    
    config:Config=Config()
    #eventually reset the config_file from args with args 
    config.load_config_from_cli_args(sys.argv[1:])
    #load using config_file eventually changer by args
    config.load_config_from_json(config.config_file)
    #update fields with args 
    config.load_config_from_cli_args(sys.argv[1:])

    
    sys.stdout = open(config.log_file, 'a')
    sys.stderr = sys.stdout

    # Charger les périphériques depuis le fichier JSON
    devices = load_devices_from_json(config.devices_file)
    
    if not devices:
        print(f"Aucun périphérique chargé. Vérifiez le fichier {config.devices_file}")
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