#!/usr/bin/python3

import subprocess
import json
import os
import argparse
import sys
import io
from typing import Optional, Dict
from PIL import Image, ImageDraw, ImageFont
import time
import random
import requests
import logging

CONFIG_FILE = os.path.expanduser('~/.config/e-zshot/config.json')  # Local config path
FONT_PATH = os.path.join(os.path.dirname(__file__), 'fonts', 'impact.ttf')  # Local font path
LOG_FILE = os.path.expanduser('~/.config/e-zshot/e-zshot.log')
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def log_message(level: int, message: str) -> None:
    """Log a message to the log file."""
    if level == logging.DEBUG:
        logging.debug(message)
    elif level == logging.INFO:
        logging.info(message)
    elif level == logging.WARNING:
        logging.warning(message)
    elif level == logging.ERROR:
        logging.error(message)
    elif level == logging.CRITICAL:
        logging.critical(message)
    else:
        logging.info(message)

def check_wayland() -> None:
    """Check if the session is using Wayland."""
    display_server = os.environ.get('XDG_SESSION_TYPE')
    if display_server != 'wayland':
        notify_and_exit("This script is intended to be used with Wayland.")

def notify_and_exit(message: str) -> None:
    """Send a notification and exit the program."""
    subprocess.run(['notify-send', "Warning", message])
    print(f"Warning: {message}")
    log_message(logging.ERROR, message)
    sys.exit(1)

def ensure_config_file_exists(config_file: str, verbose: bool) -> None:
    """Ensure the configuration file exists, creating it if not."""
    os.makedirs(os.path.dirname(config_file), exist_ok=True)
    if not os.path.exists(config_file):
        with open(config_file, 'w') as f:
            json.dump({}, f)
        if verbose:
            print(f"Config file created at: {config_file}")
    elif verbose:
        print(f"Config file already exists at: {config_file}")

def load_config() -> Dict:
    """Load configuration from the config file."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_config(config: Dict) -> None:
    """Save configuration to the config file."""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)

def enter_api_key(api_key: Optional[str], config: Dict) -> None:
    """Enter API key into the configuration."""
    if not api_key or len(api_key) < 10:
        notify_and_exit("Invalid API key. Please provide a valid API key.")
    config['api_key'] = api_key
    save_config(config)

def enter_domain(domain: Optional[str], config: Dict) -> None:
    """Enter domain into the configuration."""
    if domain and not domain.startswith("https://"):
        notify_and_exit("Invalid domain. Please provide a valid domain starting with 'https://'.")
    config['domain'] = domain or "https://i.e-z.host/"
    save_config(config)

def add_text_to_image(image_data: bytes, top_text: Optional[str], bottom_text: Optional[str], text_color: str) -> bytes:
    """Add centered text to the top and/or bottom of the screenshot."""
    with Image.open(io.BytesIO(image_data)).convert("RGBA") as img:
        draw = ImageDraw.Draw(img)
        img_width, img_height = img.size

        # Define minimum and maximum font sizes
        min_font_size = 20
        max_font_size = 80

        # Calculate font size based on image dimensions, ensuring it's within bounds
        font_size = max(min(img_width // 15, img_height // 15), min_font_size)
        font_size = min(font_size, max_font_size)
        font = ImageFont.truetype(FONT_PATH, font_size)

        # Function to draw text
        def draw_text(text: str, y_position: int) -> None:
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]

            # Centering
            text_x = (img_width - text_width) // 2
            text_y = y_position

            draw.text((text_x, text_y), text, font=font, fill=text_color)

        # Draw top text if provided
        if top_text:
            top_margin = img_height // 20  # Margin from the top of the image
            draw_text(top_text, top_margin)

        # Draw bottom text if provided
        if bottom_text:
            bottom_margin = img_height - img_height // 20 - font_size  # Margin from the bottom of the image
            draw_text(bottom_text, bottom_margin)

        # Convert back to 'RGB' before saving to avoid transparency issues
        img = img.convert("RGB")

        output = io.BytesIO()
        img.save(output, format='PNG')
        return output.getvalue()

def save_to_disk(directory: str, file_name: str, data: bytes) -> None:
    """Save data to disk as a file."""
    try:
        file_path = os.path.join(directory, file_name)
        with open(file_path, 'wb') as file:
            file.write(data)
        print(f"Screenshot saved to {file_path}")
    except IOError as e:
        notify_and_exit(f"Error saving screenshot: {e}")

def take_screenshot(full_screen: bool, verbose: bool) -> bytes:
    """Take a screenshot using Grim."""
    try:
        if verbose:
            print("Starting screenshot process...")

        if full_screen:
            command = ['grim', '-t', 'png', '-l', '0', '-']
            if verbose:
                print("Taking full screen screenshot...")
        else:
            if verbose:
                print("Launching slurp to select area...")
            slurp_result = subprocess.run(['slurp'], capture_output=True, text=True, check=True)
            geometry = slurp_result.stdout.strip()
            if verbose:
                print(f"Selected area: {geometry}")

            if not geometry:
                raise ValueError("No area selected")
            command = ['grim', '-g', geometry, '-t', 'png', '-l', '0', '-']
            if verbose:
                print("Taking selected area screenshot...")

        result = subprocess.run(command, capture_output=True, check=True)
        
        if verbose:
            print("Screenshot taken successfully.")
        return result.stdout
    except subprocess.CalledProcessError as e:
        notify_and_exit(f"Error taking screenshot: {e.stderr.decode().strip()}")
    except ValueError as e:
        notify_and_exit(f"ValueError: {str(e)}")

def upload_screenshot(data: bytes, api_key: str, verbose: bool) -> Optional[str]:
    """Upload the screenshot to e-z synchronously."""
    max_retries = 3
    base_timeout = 5  # Base timeout in seconds, reduced from 10 to 5 for efficiency

    for attempt in range(max_retries):
        try:
            if verbose:
                print(f"Starting upload (attempt {attempt + 1})...")

            start_time = time.time()  # Record the start time

            headers = {"key": api_key}
            files = {'file': ('screenshot.png', data, 'image/png')}
            
            response = requests.post("https://api.e-z.host/files", headers=headers, files=files, timeout=base_timeout * (attempt + 1))
            response.raise_for_status()

            end_time = time.time()  # Record the end time
            upload_duration = end_time - start_time  # Calculate the duration

            if verbose:
                print(f"Upload successful in {upload_duration:.2f} seconds")

            response_json = response.json()
            return response_json.get('imageUrl')

        except requests.HTTPError as e:
            if verbose:
                print(f"HTTP Error: Status {response.status_code}, Message: {response.text}")
            notify_and_exit(f"HTTP Error {response.status_code}: {response.text}")
        except requests.RequestException as e:
            error_message = str(e)
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt + random.uniform(0, 1)  # Exponential backoff with jitter
                if verbose:
                    print(f"Upload failed: {error_message}. Retrying in {wait_time:.2f} seconds...")
                time.sleep(wait_time)
            else:
                if verbose:
                    print(f"Response: {response.text if response else 'No response'}")
                notify_and_exit(f"Error uploading screenshot after {max_retries} attempts: {error_message}")
        except Exception as e:
            if verbose:
                print(f"Unexpected error: {e}")
                traceback.print_exc()
            notify_and_exit(f"Unexpected error: {e}")

def main():
    check_wayland()

    parser = argparse.ArgumentParser(description="Screenshot tool that uploads to the E-Z Hosting API.")
    parser.add_argument('-a', '--api-key', type=str, help="Enter API key")
    parser.add_argument('-d', '--domain', type=str, help="Enter the domain to be used")
    parser.add_argument('-s', '--save-dir', type=str, help="Directory to save screenshot")
    parser.add_argument('-f', '--full-screen', action='store_true', help="Capture full screen instead of selected area")
    parser.add_argument('-v', '--verbose', action='store_true', help="Enable verbose logging for debugging")
    parser.add_argument('-t', '--top-text', type=str, help="Text to display at the top of the screenshot")
    parser.add_argument('-b', '--bottom-text', type=str, help="Text to display at the bottom of the screenshot")
    parser.add_argument('-c', '--colour', type=str, default='black', help="Text color (e.g., 'black', 'white', 'red')")

    args = parser.parse_args()

    # Ensure the config file exists
    ensure_config_file_exists(CONFIG_FILE, args.verbose)

    verbose = args.verbose

    config = load_config()

    if args.api_key:
        enter_api_key(args.api_key, config)

    if args.domain:
        enter_domain(args.domain, config)

    api_key = config.get('api_key')
    domain = config.get('domain')

    if not api_key:
        parser.print_help()
        subprocess.run(['notify-send', "Please provide an API key using the '-a' option."])
        log_message(logging.ERROR, "API key is missing.")
        exit(1)

    NEW_BASE_URL = domain if domain else "https://i.e-z.host/"

    screenshot_data = take_screenshot(args.full_screen, verbose)
    log_message(logging.INFO, "Screenshot taken successfully.")

    screenshot_data = add_text_to_image(screenshot_data, args.top_text, args.bottom_text, args.colour)

    image_url = upload_screenshot(screenshot_data, api_key, verbose)
    log_message(logging.INFO, f"Image URL: {image_url}")

    if not image_url or image_url == "null":
        log_message(logging.ERROR, "Image URL is empty or null.")
        subprocess.run(['notify-send', "Error", "Image URL is empty or null."])
        exit(1)

    unique_id = image_url.split('/')[-1]

    if args.save_dir:
        if os.path.isdir(args.save_dir) and os.access(args.save_dir, os.W_OK):
            save_to_disk(args.save_dir, f"{unique_id}.png", screenshot_data)
        else:
            log_message(logging.ERROR, "Invalid directory or permission denied.")
            print("Invalid directory or permission denied.")
            exit(1)

    new_image_url = NEW_BASE_URL + unique_id

    subprocess.run(['wl-copy'], input=new_image_url.encode())
    subprocess.run(['notify-send', "Screenshot uploaded", f"URL: {new_image_url}"])

    log_message(logging.INFO, f"Screenshot URL: {new_image_url}")

if __name__ == "__main__":
    main()
