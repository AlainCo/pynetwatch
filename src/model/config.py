from typing import Any
import sys
from pathlib import Path
import json
#configuration component
# part of his values are default values for Device   
class Config:
    def __init__(self):
        # Valeurs par défaut
        self.config_file='pynetwatch-config.json'
        self.config_create=False
        self.devices_file='devices.json'
        self.devices_file_out='nul:'
        self.log_file='nul:'
        self.speech_interval=10.0
        self.speech_speed = 140
        self.speech_volume=1.0
        self.speech_voice='english'
        self.speech_text_all_is_reachable='all is reachable'
        self.speech_text_unreachable='unreachable'
        self.log_message_reconnected='reconnected'
        self.log_message_unreachable_for='unavailable for'
        self.log_message_reachable='reachable'
        self.log_message_unreachable='unreachable'
        self.gui_title='Network Monitor'
        self.gui_heading_status='Status'
        self.gui_heading_downtime="Downtime"
        self.gui_button_show_logs="Show logs"
        self.gui_button_hide_logs="Hide logs"
        self.gui_message_status_alert="Serious problems detected"
        self.gui_message_status_warn="Minor problems detected"
        self.gui_message_status_ok="All is OK"
        
        self.interval = 10.0
        self.failed_accelerate=1.0
        self.accelerate=1.0
        self.ping_count = 2
        self.ping_timeout = 1
        self.http_timeout = 3
        self.http_retry = 2
        self.ssh_key_file='ssh.key'
        self.ssh_key_password='password'
        self.ssh_retry=1
        self.ssh_timeout=10
        self.ssh_decelerate=10.0
        self.ssh_failed_accelerate=10.0
        self.ssh_obsolete=False
        
    @staticmethod
    def load():
        config=Config()
        #eventually reset the config_file from args 
        config.load_from_cli_args(sys.argv[1:])
        #load using config_file eventually changed by args
        config.load_from_json(config.config_file)
        #update fields from args 
        config.load_from_cli_args(sys.argv[1:])
        return config
        
    def load_from_json(self, filename:str) -> None:
        file_path = Path(filename)
        self.config_folder=file_path.parent
        # create config file if not exist and "config_create"  is true
        if not file_path.exists():
            if self.config_create:
                self.save_as_json(file_path)
            else:
                exit(2)
        
        # load config as JSON
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for key, value in data.items():
                if hasattr(self, key):  # Ne met à jour que les attributs existants
                    setattr(self, key, value)

    def save_as_json(self, file_path: Path) -> None:
        default_data = {key: getattr(self, key) for key in vars(self)}
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(default_data, f, indent=4)
                
    def load_from_cli_args(self, args: list[str] = sys.argv[1:]) -> None:
        for arg in args:
            if self._is_valid_arg(arg):
                key, value = self._parse_arg(arg)
                self._set_config_value(key, value)

    def _is_valid_arg(self, arg: str) -> bool:
        return arg.startswith('--') and '=' in arg and len(arg.split('=')) == 2

    def _parse_arg(self, arg: str) -> tuple[str, str]:
        key_value = arg[2:].split('=', 1)
        return key_value[0].strip().replace('-', '_'), key_value[1].strip()

    def _set_config_value(self, key: str, str_value: str) -> None:
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
            print(f"Warning: unknown key in config : {key}")

    def _convert_value(self, value: str, target_type: type) -> Any:
        if target_type == bool:
            return self._convert_to_bool(value)
        try:
            return target_type(value)
        except ValueError:
            # for float as int
            if target_type == float and '.' not in value:
                return float(value)
            raise ValueError(f"Unable to convert '{value}' into {target_type.__name__}")

    def _convert_to_bool(self, value: str) -> bool:
        true_values = ['true', '1', 'yes', 'on', 't', 'y']
        false_values = ['false', '0', 'no', 'off', 'f', 'n']
        lower_val = value.lower()
        
        if lower_val in true_values:
            return True
        if lower_val in false_values:
            return False
        raise ValueError(f"Unknown boolean value: {value}")
