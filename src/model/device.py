from __future__ import annotations
from typing import Optional
from model import Config
from pathlib import Path
import json

# objet metier pour les device à surveiller
class Device:
    def __init__(
        self,
        name: str,
        ip: Optional[str] = None,
        url: Optional[str] = None,
        is_important: bool = False,
        interval:float=30.0,
        ping_count:int=1,
        ping_timeout:int=1,
        http_timeout:int=30,
        http_retry:int=1,
        accelerate:float=1.0,
        failed_accelerate:float=1.0,
        ssh_key_file:Optional[str]=None,
        ssh_key_password:Optional[str]=None,
        ssh_host:Optional[str]=None,
        ssh_user:Optional[str]=None,
        ssh_command:Optional[str]=None,
        ssh_pattern_required:list[str]=[],
        ssh_pattern_forbiden:list[str]=[],
        ssh_retry:Optional[int]=1,
        ssh_timeout:int=30,
        ssh_user_password:Optional[str]=None,
        ssh_obsolete:bool=False
    ):
        self.name: str = name
        self.ip: Optional[str] = ip
        self.url: Optional[str] = url
        self.is_important: bool = is_important
        self.interval = interval
        self.ping_count = ping_count
        self.ping_timeout = ping_timeout
        self.http_timeout = http_timeout
        self.http_retry = http_retry
        self.accelerate=accelerate
        self.failed_accelerate=failed_accelerate
        self.ssh_key_file=ssh_key_file
        self.ssh_key_password=ssh_key_password
        self.ssh_host=ssh_host
        self.ssh_user=ssh_user
        self.ssh_command=ssh_command
        self.ssh_pattern_required=ssh_pattern_required
        self.ssh_pattern_forbiden=ssh_pattern_forbiden
        self.ssh_retry=ssh_retry
        self.ssh_timeout=ssh_timeout
        self.ssh_user_password=ssh_user_password
        self.ssh_obsolete=ssh_obsolete
        
        
    @staticmethod   
    def load(config:Config)->list[Device]:
        devices:list[Device] = []
        try:
            file_path = Path(config.devices_file)
            if not file_path.exists():
                raise FileNotFoundError(f"Fichier {config.devices_file} introuvable")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            for item in data:
                if 'name' not in item:
                    print(f"Erreur: Entrée invalide dans le JSON - clé 'name' manquante: {item}")
                    continue
                    
                devices.append(
                    Device(
                        name=item['name'],
                        ip=item.get('ip'),
                        url=item.get('url'),
                        is_important=item.get('is_important', False),
                        interval=item.get('interval', config.interval),
                        accelerate=item.get('accelerate', config.accelerate),
                        failed_accelerate=item.get('failed_accelerate', config.failed_accelerate),
                        ping_count=item.get('ping_count', config.ping_count),
                        ping_timeout=item.get('ping_timeout', config.ping_timeout),
                        http_timeout=item.get('http_timeout', config.http_timeout),
                        http_retry=item.get('http_retry', config.http_retry),
                        ssh_key_file=item.get('ssh_key_file',config.ssh_key_file),
                        ssh_key_password=item.get('ssh_key_password',config.ssh_key_password),
                        ssh_host=item.get('ssh_host',None),
                        ssh_user=item.get('ssh_user',None),
                        ssh_command=item.get('ssh_command',None),
                        ssh_pattern_required=item.get('ssh_pattern_required',[]),
                        ssh_pattern_forbiden=item.get('ssh_pattern_forbiden',[]),
                        ssh_retry=item.get('ssh_retry',config.ssh_retry),
                        ssh_timeout=item.get('ssh_timeout',config.ssh_timeout),
                        ssh_user_password=item.get('ssh_user_password',None),
                        ssh_obsolete=item.get('ssh_obsolete',False)  
                ))
            return devices
        except json.JSONDecodeError as e:
            print(f"Erreur de parsing JSON: {e}")
            return []
        except Exception as e:
            print(f"Erreur de chargement: {str(e)}")
            return []