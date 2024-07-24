#!/usr/bin/python3

import subprocess
import requests
import sys
import time
import random
import shutil
import json
import os
import logging
import argparse

CONFIG_FILE = os.path.expanduser('~/.config/e-zshot/config.json')

# Configure logging
def configure_logging(verbose: bool) -> None:
    """Configure logging based on verbosity setting."""
    logging.basicConfig(level=logging.DEBUG if verbose else logging.WARNING,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def notify(message: str) -> None:
    """Send a desktop notification."""
    subprocess.run(['notify-send', "E-ZShot", message])

def load_config() -> dict:
    """Load the configuration file."""
    if not os.path.exists(CONFIG_FILE):
        notify("Configuration file missing. Please use the Go client to set up.")
        print("Configuration file missing. Please use the Go client to set up.")
        sys.exit(1)

    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)

    if 'api_key' not in config or 'domain' not in config:
        notify("Configuration incomplete. Please use the Go client to set up.")
        print("Configuration incomplete. Please use the Go client to set up.")
        sys.exit(1)

    return config

def take_screenshot(full_screen: bool) -> bytes:
    """Take a screenshot and return it as bytes."""
    try:
        if full_screen:
            command = ['grim', '-t', 'png', '-l', '0', '-']
        else:
            slurp_result = subprocess.run(['slurp'], capture_output=True, text=True, check=True)
            geometry = slurp_result.stdout.strip()
            if not geometry:
                raise ValueError("No area selected")
            command = ['grim', '-g', geometry, '-t', 'png', '-l', '0', '-']
        
        result = subprocess.run(command, capture_output=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        logging.error(f"Error taking screenshot: {e.stderr.strip()}")
        notify(f"Error taking screenshot: {e.stderr.strip()}")
        print(f"Error taking screenshot: {e.stderr.strip()}")
        sys.exit(1)
    except ValueError as e:
        logging.error(f"Error: {e}")
        notify(f"Error: {e}")
        print(f"Error: {e}")
        sys.exit(1)

def upload_screenshot(data: bytes, api_key: str, domain: str) -> str:
    """Upload the screenshot and return the URL."""
    if not api_key or not domain:
        notify("Configuration incomplete. Please use the Go client to set up.")
        print("Configuration incomplete. Please use the Go client to set up.")
        sys.exit(1)
    
    max_retries = 3
    base_timeout = 5

    for attempt in range(max_retries):
        try:
            headers = {"key": api_key}
            files = {'file': ('screenshot.png', data, 'image/png')}
            
            response = requests.post("https://api.e-z.host/files", headers=headers, files=files, timeout=base_timeout * (attempt + 1))
            response.raise_for_status()

            response_json = response.json()
            return response_json.get('imageUrl')

        except requests.RequestException as e:
            logging.error(f"Upload failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt + random.uniform(0, 1))
            else:
                notify(f"Upload failed: {e}")
                print(f"Upload failed: {e}")
                sys.exit(1)

def copy_to_clipboard(text: str) -> None:
    """Copy the text to the clipboard."""
    if shutil.which('wl-copy'):
        subprocess.run(['wl-copy'], input=text.encode())
    elif shutil.which('xclip'):
        subprocess.run(['xclip', '-selection', 'clipboard'], input=text.encode())
    else:
        notify("Clipboard copy utility not found.")
        print("Clipboard copy utility not found.")

def mask_api_key(api_key: str) -> str:
    """Mask the API key, censoring characters after the underscore."""
    parts = api_key.split('_')
    if len(parts) > 1:
        return parts[0] + '_' + '*' * (len(parts[1]) - 3) + parts[1][-3:]
    return api_key

def main():
    parser = argparse.ArgumentParser(description="Screenshot tool that uploads to an external server.")
    parser.add_argument('--full-screen', action='store_true', help="Take a full-screen screenshot")
    parser.add_argument('--save-to-disk', action='store_true', help="Save the screenshot to disk")
    parser.add_argument('--upload-to-api', action='store_true', help="Upload the screenshot to API")
    parser.add_argument('--verbose', action='store_true', help="Enable verbose logging")

    args = parser.parse_args()

    full_screen = args.full_screen
    save_to_disk = args.save_to_disk
    upload_to_api = args.upload_to_api
    verbose = args.verbose

    config = load_config()
    api_key = config['api_key']
    domain = config['domain']
    text_plugin_enabled = config.get('text_plugin_enabled', False)
    
    configure_logging(verbose)

    screenshot_data = take_screenshot(full_screen)

    if save_to_disk:
        # Save the screenshot to disk
        with open('screenshot.png', 'wb') as f:
            f.write(screenshot_data)
        notify("Screenshot saved to disk.")
        print("Screenshot saved to disk.")
    
    if upload_to_api:
        image_url = upload_screenshot(screenshot_data, api_key, domain)
        if not image_url:
            notify("Error: Empty or null image URL.")
            print("Error: Empty or null image URL.")
            sys.exit(1)

        final_url = f"{domain.rstrip('/')}/{image_url.split('/')[-1]}"
        copy_to_clipboard(final_url)
        masked_api_key = mask_api_key(api_key)
        if verbose:
            notify(f"Screenshot uploaded. URL: {final_url}")
            print(f"Screenshot URL: {final_url} (API Key: {masked_api_key})")
        else:
            notify(f"Screenshot uploaded. URL: {final_url}")
            print(f"Screenshot URL: {final_url}")
    else:
        notify("Screenshot not uploaded.")
        print("Screenshot not uploaded.")

if __name__ == "__main__":
    main()
