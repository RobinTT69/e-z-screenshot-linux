import subprocess
import requests
import argparse
import json
import os
import sys
import logging
import time

CONFIG_FILE = os.path.expanduser('~/.config/e-zshot/config.json')
UPLOAD_URL = "https://api.e-z.host/files"

def configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(level=level, format='%(message)s')

def notify(message: str) -> None:
    subprocess.run(['notify-send', "E-ZShot", message])

def load_config() -> dict:
    if not os.path.exists(CONFIG_FILE):
        notify("Configuration file missing. Please set it up.")
        sys.exit(1)

    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)

    if 'api_key' not in config or 'domain' not in config:
        notify("Configuration incomplete. Please set it up.")
        sys.exit(1)

    return config

def take_screenshot(fullscreen: bool, filename: str) -> None:
    command = ['gnome-screenshot']
    
    if fullscreen:
        command.extend(['--file', filename])
    else:
        command.extend(['--file', filename, '--area'])
    
    try:
        subprocess.run(command, check=True)
        print(f"Screenshot saved as {filename}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error taking screenshot: {e}")
        notify(f"Error taking screenshot: {e}")
        sys.exit(1)

def upload_screenshot(filepath: str, api_key: str, domain: str) -> str:
    if not api_key or not domain:
        notify("Configuration incomplete. Please set it up.")
        sys.exit(1)

    max_retries = 3
    base_timeout = 5

    with open(filepath, 'rb') as f:
        file_data = f.read()

    logging.debug("Uploading screenshot...")
    print("Uploading", end="", flush=True)

    for attempt in range(max_retries):
        try:
            headers = {"key": api_key}
            files = {'file': ('screenshot.png', file_data, 'image/png')}
            
            response = requests.post(UPLOAD_URL, headers=headers, files=files, timeout=base_timeout * (attempt + 1))
            response.raise_for_status()

            print("\rUpload complete!", flush=True)
            logging.debug("Upload successful.")
            response_json = response.json()
            return response_json.get('imageUrl')

        except requests.RequestException as e:
            logging.error(f"Upload attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                print(".", end="", flush=True)
                time.sleep(2 ** attempt + random.uniform(0, 1))
            else:
                print("\nUpload failed.")
                notify(f"Upload failed: {e}")
                sys.exit(1)

def copy_to_clipboard(text: str) -> None:
    try:
        subprocess.run(['xclip', '-selection', 'clipboard'], input=text.encode(), check=True)
        logging.debug("URL copied to clipboard.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error copying to clipboard: {e}")

def main():
    parser = argparse.ArgumentParser(description="Take a screenshot and upload it to an API.")
    parser.add_argument('-v', '--verbose', action='store_true', help="Enable verbose logging")
    parser.add_argument('--fullscreen', action='store_true', help="Capture the entire screen")
    parser.add_argument('--filename', type=str, default='/tmp/screenshot.png', help="Filename to save the screenshot")
    parser.add_argument('--no-upload', action='store_true', help="Disable uploading the screenshot to API")

    args = parser.parse_args()
    configure_logging(args.verbose)

    config = load_config()
    api_key = config['api_key']
    domain = config['domain']

    take_screenshot(args.fullscreen, args.filename)

    if not args.no_upload:
        start_time = time.time()
        image_url = upload_screenshot(args.filename, api_key, domain)
        elapsed_time = time.time() - start_time

        if not image_url:
            notify("Error: Empty or null image URL.")
            sys.exit(1)

        final_url = f"https://{domain.rstrip('/')}/{image_url.split('/')[-1]}"
        print(f"Screenshot URL: {final_url} (took {elapsed_time:.2f}s)")
        notify(f"Screenshot uploaded. URL: {final_url}")

        # Copy URL to clipboard
        copy_to_clipboard(final_url)
    else:
        logging.debug("Screenshot not uploaded.")

if __name__ == '__main__':
    main()
