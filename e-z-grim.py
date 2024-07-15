#!/usr/bin/python3
import subprocess
import requests
import json
import os
import argparse
import sys
import io
from typing import Optional, Dict
from PIL import Image, ImageDraw, ImageFont

CONFIG_FILE = os.path.expanduser('~/.config/e-zshot/config.json')
FONT_PATH = os.path.join(os.path.dirname(__file__), 'fonts', 'impact.ttf')  # Local font path

def check_wayland() -> None:
    """Check if the session is using Wayland."""
    display_server = os.environ.get('XDG_SESSION_TYPE')
    if display_server != 'wayland':
        notify_and_exit("This script is intended to be used with Wayland.")

def notify_and_exit(message: str) -> None:
    """Send a notification and exit the program."""
    subprocess.run(['notify-send', "Warning", message])
    print(f"Warning: {message}")
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

def add_text_to_image(image_data: bytes, top_text: Optional[str], bottom_text: Optional[str], use_frame: bool) -> bytes:
    """Add centered text with an optional black frame to the top and/or bottom of the screenshot."""
    with Image.open(io.BytesIO(image_data)) as img:
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(FONT_PATH, 40)

        # Function to draw text with optional frame
        def draw_text_with_frame(text: str, position: tuple, is_bottom: bool) -> None:
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]

            # Centering
            text_x = (img.width - text_width) // 2
            text_y = position[1]

            if use_frame:
                frame_position = (text_x - 10, text_y - (text_height // 2) - 10, text_x + text_width + 10, text_y + (text_height // 2) + 10)
                draw.rectangle(frame_position, fill="black")  # Draw black frame
            
            draw.text((text_x, text_y - (text_height // 2)), text, font=font, fill="white")  # Center the text

        if top_text:
            draw_text_with_frame(top_text, (0, 10), is_bottom=False)

        if bottom_text:
            text_bbox = draw.textbbox((0, 0), bottom_text, font=font)
            text_height = text_bbox[3] - text_bbox[1]
            bottom_position = (img.height - text_height - 10)
            draw_text_with_frame(bottom_text, (0, bottom_position), is_bottom=True)

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
        if full_screen:
            result = subprocess.run(['grim', '-t', 'png', '-l', '0', '-'], capture_output=True, check=True)
        else:
            slurp_result = subprocess.run(['slurp'], capture_output=True, text=True, check=True)
            geometry = slurp_result.stdout.strip()
            if not geometry:
                raise ValueError("No area selected")
            result = subprocess.run(['grim', '-g', geometry, '-t', 'png', '-l', '0', '-'], capture_output=True, check=True)

        if verbose:
            print("Screenshot taken successfully.")
        return result.stdout
    except subprocess.CalledProcessError as e:
        notify_and_exit(f"Error taking screenshot: {e}")
    except ValueError as e:
        notify_and_exit(str(e))

def upload_screenshot(data: bytes, api_key: str, verbose: bool) -> Optional[str]:
    """Upload the screenshot to a remote server."""
    try:
        if verbose:
            print("Starting upload...")
        response = requests.post(
            "https://api.e-z.host/files",
            headers={"key": api_key},
            files={"file": ("screenshot.png", data, "image/png")},
            timeout=10
        )
        response.raise_for_status()
        if verbose:
            print("Upload successful")
        return response.json().get('imageUrl')
    except requests.RequestException as e:
        notify_and_exit(f"Error uploading screenshot: {e}")

def main():
    check_wayland()

    parser = argparse.ArgumentParser(description="Screenshot tool that uploads to an external server.")
    parser.add_argument('-a', '--api-key', type=str, help="Enter API key")
    parser.add_argument('-d', '--domain', type=str, help="Enter the domain to be used")
    parser.add_argument('-s', '--save-dir', type=str, help="Directory to save screenshot")
    parser.add_argument('-f', '--full-screen', action='store_true', help="Capture full screen instead of selected area")
    parser.add_argument('-v', '--verbose', action='store_true', help="Enable verbose logging for debugging")
    parser.add_argument('--top-text', type=str, help="Text to display at the top of the screenshot")
    parser.add_argument('--bottom-text', type=str, help="Text to display at the bottom of the screenshot")
    parser.add_argument('--use-frame', action='store_true', help="Use a black frame around the text (only if text is provided)")

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
        subprocess.run(['notify-send', "Please provide an API key using the '-A' option."])
        exit(1)

    NEW_BASE_URL = domain if domain else "https://i.e-z.host/"

    screenshot_data = take_screenshot(args.full_screen, verbose)

    if verbose:
        print(f"API Key: {api_key}")
        print(f"Domain: {NEW_BASE_URL}")

    # Call the modified function with the use_frame argument
    screenshot_data = add_text_to_image(screenshot_data, args.top_text, args.bottom_text, args.use_frame)

    imageUrl = upload_screenshot(screenshot_data, api_key, verbose)

    if not imageUrl or imageUrl == "null":
        print("Error: Image URL is empty or null.")
        subprocess.run(['notify-send', "Error", "Image URL is empty or null."])
        exit(1)

    unique_id = imageUrl.split('/')[-1]

    if args.save_dir:
        if os.path.isdir(args.save_dir) and os.access(args.save_dir, os.W_OK):
            save_to_disk(args.save_dir, f"{unique_id}", screenshot_data)
        else:
            print("Invalid directory or permission denied.")
            exit(1)

    new_image_url = NEW_BASE_URL + unique_id

    subprocess.run(['wl-copy'], input=new_image_url.encode())
    subprocess.run(['notify-send', "Screenshot uploaded", f"URL: {new_image_url}"])

    print(f"Screenshot URL: {new_image_url}")

if __name__ == "__main__":
    main()
