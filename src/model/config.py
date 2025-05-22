from typing import Any
import sys
from pathlib import Path
import json
#composant representant la configuration de la surveillance        
class Config:
    def __init__(self):
        # Valeurs par défaut
        self.speech_speed = 140
        self.speech_volume=1.0
        self.interval = 10.0
        self.failed_accelerate=1.0
        self.accelerate=1.0
        self.ping_count = 2
        self.ping_timeout = 1
        self.http_timeout = 3
        self.http_retry = 2
        self.log_file='nul:'
        self.devices_file='devices.json'
        self.config_file='pynetwatch-config.json'
        self.config_create=False
        self.ssh_key_file='ssh.key'
        self.ssh_key_password='password'
        self.ssh_retry=1
        self.ssh_timeout=3
        self.ssh_decelerate=10.0
        self.ssh_failed_accelerate=10.0
        self.ssh_obsolete=False
        

    @staticmethod
    def load():
        config=Config()
        #eventually reset the config_file from args with args 
        config.load_config_from_cli_args(sys.argv[1:])
        #load using config_file eventually changer by args
        config.load_config_from_json(config.config_file)
        #update fields with args 
        config.load_config_from_cli_args(sys.argv[1:])
        return config
        
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
