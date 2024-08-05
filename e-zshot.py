#!/usr/bin/python3

import json
import os
import subprocess
import sys

# Adjust this path based on where the configuration file is installed
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

def find_script(script_name: str) -> str:
    """Find the script with .py extension or fallback to without .py."""
    # Define the paths to search for the scripts
    possible_paths = [
        os.path.join(os.path.dirname(__file__), 'plugins', script_name + '.py'),
        os.path.join(os.path.dirname(__file__), 'plugins', script_name),
        os.path.join('/usr/bin', script_name + '.py'),
        os.path.join('/usr/bin', script_name)
    ]
    
    for path in possible_paths:
        if os.path.isfile(path):
            return path

    return None

def main():
    config = load_config()
    screenshot_tool = config.get('screenshot_tool', 'flameshot')
    
    script_name = ''
    if screenshot_tool == 'flameshot':
        script_name = 'e-z-flameshot'
    elif screenshot_tool == 'grim':
        script_name = 'e-z-grim'
    elif screenshot_tool == 'gnome':
        script_name = 'e-z-gnome'
    else:
        print(f"Unsupported screenshot tool: {screenshot_tool}")
        sys.exit(1)

    # Find the script
    script_path = find_script(script_name)
    
    if not script_path:
        print(f"Script {script_name} not found.")
        sys.exit(1)

    # If the script has a .py extension, run it with python3, otherwise execute it directly
    if script_path.endswith('.py'):
        subprocess.run(['python3', script_path] + sys.argv[1:])
    else:
        subprocess.run([script_path] + sys.argv[1:])

if __name__ == "__main__":
    main()
