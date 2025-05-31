from __future__ import annotations
from typing import Optional,Any
from model import Config
from pathlib import Path
import json

# object representing devices to watch
class Device:
    def __init__(
        self,
        data: dict[str,Any],
        config: Config
    ):
        self.name:str=""
        self.config_folder=Path(".")
        self.ip: Optional[str] =None
        self.url: Optional[str] =None
        self.is_important: bool=False
        self.interval :float=10.0
        self.ping_count :int=1
        self.ping_timeout :int=1
        self.http_timeout :int=1
        self.http_retry :int=1
        self.accelerate:float=1.0
        self.failed_accelerate:float=1.0
        self.ssh_key_file:Optional[str]=None
        self.ssh_key_folder:Optional[str]=None
        self.ssh_key_password:Optional[str]=None
        self.ssh_host:Optional[str]=None
        self.ssh_user:Optional[str]=None
        self.ssh_command:Optional[str]=None
        self.ssh_pattern_required:list[str]=[]
        self.ssh_pattern_forbiden:list[str]=[]
        self.ssh_retry:int=1
        self.ssh_timeout:int=1
        self.ssh_user_password:Optional[str]=None
        self.ssh_obsolete:bool=False
        self.ssh_allow_agent:bool=True
        self.ssh_decelerate:float=1.0
        self.ssh_failed_accelerate:float=1.0
        
        for attr in vars(config):
            if not attr.startswith('__') and hasattr(self, attr):
                setattr(self, attr, getattr(config, attr))
        for key, value in data.items():
            if hasattr(self, key):  # Ne met à jour que les attributs existants
                setattr(self, key, value)

    @staticmethod   
    def load(config:Config)->list[Device]:
        devices:list[Device] = []
        try:
            file_path = Path(config.config_folder,config.devices_file)
            if not file_path.exists():
                raise FileNotFoundError(f"Fichier {config.devices_file} introuvable")
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for item in data:
                if 'name' not in item:
                    print(f"Invalid Device entry, missing 'name': {item}")
                    continue
                devices.append(
                    Device(
                        item,
                        config
                        )
                )
            return devices
        except json.JSONDecodeError as e:
            print(f"Device JSON parsing error: {e}")
            return []
        except Exception as e:
            print(f"Device Loading error: {str(e)}")
            return []
    
    @staticmethod     
    def save(devices:list[Device], config:Config) -> None:
        data:list[dict[str,Any]]=[]
        for device in devices:
            item:dict[str,Any]=dict()
            for attr in vars(device):
                if not attr.startswith('__') and hasattr(device, attr):
                    item[attr]= getattr(device, attr)
            data.append(item)
        if config.devices_file_out:
            try:
                file_path = Path(config.config_folder,config.devices_file_out)
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=4)
            except Exception as e:
                print(f"Device save error {str(e)}")