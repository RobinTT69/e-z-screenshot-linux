#!/usr/bin/python3

import json
import os
import subprocess
import sys

CONFIG_FILE = os.path.expanduser('~/.config/e-zshot/config.json')

def load_config() -> dict:
    """Load the configuration file."""
    if not os.path.exists(CONFIG_FILE):
        print("Configuration file missing. Please use the Go client to set up.")
        sys.exit(1)

    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)

    if 'screenshot_tool' not in config:
        config['screenshot_tool'] = 'flameshot'  # Default to flameshot

    return config

def main():
    config = load_config()
    screenshot_tool = config.get('screenshot_tool', 'flameshot')

    if screenshot_tool == 'flameshot':
        subprocess.run(['python3', 'plugins/e-z-flameshot.py'])
    elif screenshot_tool == 'grim':
        subprocess.run(['python3', 'plugins/e-z-grim.py'])
    else:
        print(f"Unsupported screenshot tool: {screenshot_tool}")
        sys.exit(1)

if __name__ == "__main__":
    main()

