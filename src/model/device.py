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
        failed_accelerate:float=1.0
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
                    
                devices.append(Device(
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
                ))
            return devices
        except json.JSONDecodeError as e:
            print(f"Erreur de parsing JSON: {e}")
            return []
        except Exception as e:
            print(f"Erreur de chargement: {str(e)}")
            return []