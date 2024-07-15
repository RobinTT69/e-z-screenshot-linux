#!/usr/bin/python3

import subprocess
import requests
import json
import os
import argparse

CONFIG_FILE = os.path.expanduser('~/.config/e-zshot/config.json')

def get_config_path():
    home = os.path.expanduser("~")
    config_dir = os.path.join(home, '.config', 'e-zshot')
    config_file = os.path.join(config_dir, 'config.json')
    return config_file

def ensure_config_file_exists(config_file):
    try:
        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(config_file), exist_ok=True)
        
        # Check if the config file exists
        if not os.path.exists(config_file):
            # Create an empty config file with default settings
            with open(config_file, 'w') as f:
                json.dump({}, f)  # Initialize with an empty JSON object
            print(f"Config file created at: {config_file}")
        else:
            print(f"Config file already exists at: {config_file}")
    except Exception as e:
        print(f"Error creating config file: {e}")

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)

def enter_api_key(api_key, config):
    if not api_key or len(api_key) < 10:  # Basic validation for API key length
        print("Invalid API key. Please provide a valid API key.")
        exit(1)
    config['api_key'] = api_key
    save_config(config)

def enter_domain(domain, config):
    if not domain.startswith("https://"):
        print("Invalid domain. Please provide a valid domain starting with 'https://'.")
        exit(1)
    config['domain'] = domain
    save_config(config)

def save_to_disk(directory, file_name, data):
    try:
        file_path = os.path.join(directory, f"{file_name}")  # Append .jpeg here
        with open(file_path, 'wb') as file:
            file.write(data)
        print(f"Screenshot saved to {file_path}")
    except Exception as e:
        print(f"Error saving screenshot: {e}")
        exit(1)

def take_screenshot(full_screen):
    try:
        if full_screen:
            # Take full screen screenshot using grim
            grim_result = subprocess.run(['grim', '-t', 'jpeg', '-'], capture_output=True, check=True)
        else:
            # Get the selected area using slurp
            slurp_result = subprocess.run(['slurp'], capture_output=True, text=True, check=True)
            geometry = slurp_result.stdout.strip()
            
            if not geometry:
                raise ValueError("No area selected")

            # Take the screenshot using grim
            grim_result = subprocess.run(['grim', '-g', geometry, '-t', 'jpeg', '-'], capture_output=True, check=True)
        
        return grim_result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error taking screenshot: {e}")
        exit(1)
    except ValueError as e:
        print(e)
        exit(1)

def upload_screenshot(data, api_key):
    try:
        response = requests.post(
            "https://api.e-z.host/files",
            headers={"key": api_key},
            files={"file": ("screenshot.jpeg", data, "image/jpeg")}
        )
        response.raise_for_status()
        response_json = response.json()
        return response_json.get('imageUrl')
    except requests.RequestException as e:
        print(f"Error uploading screenshot: {e}")
        subprocess.run(['notify-send', "Error", f"Error uploading screenshot: {e}"])
        exit(1)

def main():
    config_path = get_config_path()
    ensure_config_file_exists(config_path)
    config = load_config()

    parser = argparse.ArgumentParser(description="Screenshot tool that uploads to an external server.")
    parser.add_argument('-A', '--api-key', type=str, help="Enter API key")
    parser.add_argument('-D', '--domain', type=str, help="Enter the domain to be used")
    parser.add_argument('-S', '--save-dir', type=str, help="Directory to save screenshot")
    parser.add_argument('-F', '--full-screen', action='store_true', help="Capture full screen instead of selected area")

    args = parser.parse_args()

    if args.api_key:
        enter_api_key(args.api_key, config)

    if args.domain:
        enter_domain(args.domain, config)

    api_key = config.get('api_key')
    domain = config.get('domain')

    if not api_key:
        parser.print_help()
        subprocess.run(['notify-send', "Please provide an API key using the '-A' option."])
        exit(1)

    if domain:
        NEW_BASE_URL = domain
    else:
        NEW_BASE_URL = "null"

    if NEW_BASE_URL == "null":
        print("Please replace the 'NEW_BASE_URL' variable with your domain as demonstrated in the git repo's readme.")
        subprocess.run(['notify-send', "Please replace the 'NEW_BASE_URL' variable with your domain as demonstrated in the git repo's readme."])
        exit(1)

    screenshot_data = take_screenshot(args.full_screen)

    imageUrl = upload_screenshot(screenshot_data, api_key)

    if not imageUrl or imageUrl == "null":
        print("Error: Image URL is empty or null.")
        subprocess.run(['notify-send', "Error", "Image URL is empty or null."])
        exit(1)

    # Extract unique ID from the URL
    unique_id = imageUrl.split('/')[-1]

    if args.save_dir:
        if os.path.isdir(args.save_dir) and os.access(args.save_dir, os.W_OK):
            save_to_disk(args.save_dir, f"{unique_id}", screenshot_data)  # Save without additional .jpeg
        else:
            print("Invalid directory or permission denied.")
            exit(1)

    new_image_url = NEW_BASE_URL + unique_id

    subprocess.run(['wl-copy'], input=new_image_url.encode())
    subprocess.run(['notify-send', "Screenshot uploaded", f"URL: {new_image_url}"])

    print(f"Screenshot URL: {new_image_url}")

if __name__ == "__main__":
    main()
