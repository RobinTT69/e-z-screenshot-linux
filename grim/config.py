import json
import os
from typing import Dict

CONFIG_FILE = os.path.expanduser('~/.config/e-zshot/config.json')

def ensure_config_file_exists(config_file: str, verbose: bool) -> None:
    os.makedirs(os.path.dirname(config_file), exist_ok=True)
    if not os.path.exists(config_file):
        with open(config_file, 'w') as f:
            json.dump({"plugins": []}, f)
        if verbose:
            print(f"Created config file at: {config_file}")
    elif verbose:
        print(f"Config file already exists at: {config_file}")

def load_config() -> Dict:
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            config.setdefault('file_type', 'PNG')
            config.setdefault('compression_level', 6)
            config.setdefault('plugins', [])
            return config
    return {'file_type': 'PNG', 'compression_level': 6, 'plugins': []}

def save_config(config: Dict) -> None:
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)
