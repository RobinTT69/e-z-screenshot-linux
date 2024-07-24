#!/usr/bin/python3

import subprocess
import json
import os
import argparse
import sys
import time
import random
import requests
import logging
import traceback

from plugins.TextProcessing import add_text_to_image
from plugins.Logging import log_message
from plugins.GUI import TextInputDialog

CONFIG_FILE = os.path.expanduser('~/.config/e-zshot/config.json')
LOG_FILE = os.path.expanduser('~/.config/e-zshot/e-zshot.log')
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def check_wayland() -> None:
    """Check if we're running on Wayland."""
    if os.environ.get('XDG_SESSION_TYPE') != 'wayland':
        notify_and_exit("This script works with Wayland only.")

def notify_and_exit(message: str) -> None:
    """Show a notification and exit."""
    subprocess.run(['notify-send', "Hey", message])
    print(f"Oops, {message}")
    log_message(logging.ERROR, message)
    sys.exit(1)

def ensure_config_file_exists(config_file: str, verbose: bool) -> None:
    """Create the config file if it doesn’t exist."""
    os.makedirs(os.path.dirname(config_file), exist_ok=True)
    if not os.path.exists(config_file):
        with open(config_file, 'w') as f:
            json.dump({}, f)
        if verbose:
            print(f"Created config file at: {config_file}")
    elif verbose:
        print(f"Config file already at: {config_file}")

def load_config() -> dict:
    """Load the config file."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            # Set default values if they do not exist in the config file
            config.setdefault('file_type', 'PNG')
            config.setdefault('compression_level', 6)  # Default PNG compression level (0-9)
            return config
    return {'file_type': 'PNG', 'compression_level': 6}

def save_config(config: dict) -> None:
    """Save the config file."""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

def enter_api_key(api_key: str, config: dict) -> None:
    """Save the API key."""
    if not api_key or len(api_key) < 10:
        notify_and_exit("Bad API key. Fix it and try again.")
    config['api_key'] = api_key
    save_config(config)

def enter_domain(domain: str, config: dict) -> None:
    """Save the domain."""
    if domain and not domain.startswith("https://"):
        notify_and_exit("Bad domain. Must start with 'https://'.")
    config['domain'] = domain or "https://i.e-z.host/"
    save_config(config)

def save_to_disk(directory: str, file_name: str, data: bytes, file_type: str) -> None:
    """Save the file to disk."""
    try:
        file_path = os.path.join(directory, f"{file_name}.{file_type.lower()}")
        with open(file_path, 'wb') as file:
            file.write(data)
        print(f"Saved screenshot to {file_path}")
    except IOError as e:
        notify_and_exit(f"Couldn't save screenshot: {e}")

def take_screenshot(full_screen: bool, verbose: bool) -> bytes:
    """Take a screenshot."""
    try:
        if verbose:
            print("Getting ready to take a screenshot...")

        if full_screen:
            command = ['grim', '-t', 'png', '-l', '0', '-']
            if verbose:
                print("Capturing full screen...")
        else:
            if verbose:
                print("Selecting area...")
            slurp_result = subprocess.run(['slurp'], capture_output=True, text=True, check=True)
            geometry = slurp_result.stdout.strip()
            if verbose:
                print(f"Selected area: {geometry}")

            if not geometry:
                raise ValueError("No area selected")
            command = ['grim', '-g', geometry, '-t', 'png', '-l', '0', '-']
            if verbose:
                print("Capturing selected area...")

        result = subprocess.run(command, capture_output=True, check=True)
        
        if verbose:
            print("Screenshot taken!")
        return result.stdout
    except subprocess.CalledProcessError as e:
        notify_and_exit(f"problem with screenshot: {e.stderr.strip()}")
    except ValueError as e:
        notify_and_exit(f"Error: {str(e)}")

def upload_screenshot(data: bytes, api_key: str, verbose: bool) -> Optional[str]:
    """Upload the screenshot."""
    max_retries = 3
    base_timeout = 5

    for attempt in range(max_retries):
        try:
            if verbose:
                print(f"Uploading screenshot (attempt {attempt + 1})...")

            start_time = time.time()

            headers = {"key": api_key}
            files = {'file': ('screenshot.png', data, 'image/png')}
            
            response = requests.post("https://api.e-z.host/files", headers=headers, files=files, timeout=base_timeout * (attempt + 1))
            response.raise_for_status()

            end_time = time.time()
            upload_duration = end_time - start_time

            if verbose:
                print(f"Upload complete in {upload_duration:.2f} seconds")

            response_json = response.json()
            return response_json.get('imageUrl')

        except requests.HTTPError as e:
            if verbose:
                print(f"HTTP Error: Status {response.status_code}, Message: {response.text}")
            notify_and_exit(f"HTTP Error {response.status_code}: {response.text}")
        except requests.RequestException as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt + random.uniform(0, 1)
                if verbose:
                    print(f"Upload failed: {e}. Retrying in {wait_time:.2f} seconds...")
                time.sleep(wait_time)
            else:
                if verbose:
                    print(f"Response: {response.text if response else 'No response'}")
                notify_and_exit(f"Upload failed after {max_retries} tries: {e}")
        except Exception as e:
            if verbose:
                print(f"Unexpected error: {e}")
                traceback.print_exc()
            notify_and_exit(f"Unexpected error: {e}")
    return None

def main():
    check_wayland()

    parser = argparse.ArgumentParser(description="Screenshot tool that uploads to E-Z Hosting API.")
    parser.add_argument('-a', '--api-key', type=str, help="API key")
    parser.add_argument('-d', '--domain', type=str, help="Domain to use")
    parser.add_argument('-s', '--save-dir', type=str, help="Directory to save screenshot")
    parser.add_argument('-f', '--full-screen', action='store_true', help="Capture full screen")
    parser.add_argument('-v', '--verbose', action='store_true', help="Show more info")
    parser.add_argument('-t', '--top-text', type=str, help="Text at the top of the screenshot")
    parser.add_argument('-b', '--bottom-text', type=str, help="Text at the bottom of the screenshot")
    parser.add_argument('-c', '--colour', type=str, default='white', help="Text color")
    parser.add_argument('-g', '--gui', action='store_true', help="Use graphical text input")

    parser.add_argument('-ft', '--file-type', type=str, choices=['PNG'], default='PNG', help="File type to save (PNG only)")
    parser.add_argument('-cl', '--compression-level', type=int, default=6, help="Compression level for PNG (0-9)")

    args = parser.parse_args()

    ensure_config_file_exists(CONFIG_FILE, args.verbose)

    verbose = args.verbose

    config = load_config()
    config['file_type'] = args.file_type
    config['compression_level'] = args.compression_level
    save_config(config)

    if args.api_key:
        enter_api_key(args.api_key, config)

    if args.domain:
        enter_domain(args.domain, config)

    api_key = config.get('api_key')
    domain = config.get('domain')
    file_type = config.get('file_type')
    compression_level = config.get('compression_level')

    if not api_key:
        parser.print_help()
        subprocess.run(['notify-send', "Need an API key. Use '-a' option."])
        log_message(logging.ERROR, "API key missing.")
        exit(1)

    NEW_BASE_URL = domain or "https://i.e-z.host/"

    if args.gui:
        app = QApplication(sys.argv)

        top_text_dialog = TextInputDialog(
            title="Top Text",
            label="Text for the top of the screenshot:",
            placeholder="Top text"
        )
        top_text = top_text_dialog.get_text()
        if top_text:
            args.top_text = top_text

        bottom_text_dialog = TextInputDialog(
            title="Bottom Text",
            label="Text for the bottom of the screenshot:",
            placeholder="Bottom text"
        )
        bottom_text = bottom_text_dialog.get_text()
        if bottom_text:
            args.bottom_text = bottom_text

        app.quit()

    screenshot_data = take_screenshot(args.full_screen, verbose)
    log_message(logging.INFO, "Screenshot taken.")

    screenshot_data = add_text_to_image(screenshot_data, args.top_text, args.bottom_text, args.colour, file_type, compression_level)

    image_url = upload_screenshot(screenshot_data, api_key, verbose)
    log_message(logging.INFO, f"Image URL: {image_url}")

    if not image_url or image_url == "null":
        log_message(logging.ERROR, "Empty or null image URL.")
        subprocess.run(['notify-send', "Error", "Image URL is empty or null."])
        exit(1)

    unique_id = image_url.split('/')[-1]

    if args.save_dir:
        if os.path.isdir(args.save_dir) and os.access(args.save_dir, os.W_OK):
            save_to_disk(args.save_dir, unique_id, screenshot_data, file_type)
        else:
            log_message(logging.ERROR, "Invalid directory or no write permissions.")
            print("Invalid directory or no write permissions.")
            exit(1)

    new_image_url = NEW_BASE_URL + unique_id

    subprocess.run(['wl-copy'], input=new_image_url.encode())
    subprocess.run(['notify-send', "Screenshot uploaded", f"URL: {new_image_url}"])

    log_message(logging.INFO, f"Screenshot URL: {new_image_url}")

if __name__ == "__main__":
    main()
