#!/usr/bin/python3

from PIL import Image, ImageDraw, ImageFont
import subprocess
import requests
import argparse
import logging
import random
import shutil
import uuid
import json
import time
import sys
import os
import io

CONFIG_FILE = os.path.expanduser('~/.config/e-zshot/config.json')
UPLOAD_URL = "https://api.e-z.host/files"

def configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(level=level, format='%(message)s')

def notify(message: str) -> None:
    subprocess.run(['notify-send', "E-ZShot", message])

def load_config() -> dict:
    if not os.path.exists(CONFIG_FILE):
        notify("Configuration file missing. Please use the Go client to set up.")
        sys.exit(1)

    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)

    if 'api_key' not in config or 'domain' not in config:
        notify("Configuration incomplete. Please use the Go client to set up.")
        sys.exit(1)

    return config

def detect_environment() -> str:
    wayland_env_vars = ['WAYLAND_DISPLAY', 'XDG_SESSION_TYPE']
    x11_env_vars = ['DISPLAY']

    if any(var in os.environ for var in wayland_env_vars):
        if 'WAYLAND_DISPLAY' in os.environ and os.environ['WAYLAND_DISPLAY']:
            return 'wayland'
        if 'XDG_SESSION_TYPE' in os.environ and os.environ['XDG_SESSION_TYPE'] == 'wayland':
            return 'wayland'
    
    if any(var in os.environ for var in x11_env_vars):
        return 'x11'
    
    return 'x11'

def take_screenshot(full_screen: bool) -> bytes:
    try:
        env = detect_environment()
        if full_screen:
            command = ['grim', '-t', 'png', '-l', '0', '-'] if env == 'wayland' else ['grim', '-t', 'png', '-']
            logging.debug("Taking full-screen screenshot...")
        else:
            selector = 'slurp' if env == 'wayland' else 'slop'
            logging.debug("Select area for screenshot...")
            slop_result = subprocess.run([selector], capture_output=True, text=True, check=True)
            geometry = slop_result.stdout.strip()
            if not geometry:
                raise ValueError("No area selected")
            command = ['grim', '-g', geometry, '-t', 'png', '-l', '0', '-']
        
        result = subprocess.run(command, capture_output=True, check=True)
        logging.debug("Screenshot captured successfully.")
        return result.stdout
    except subprocess.CalledProcessError as e:
        logging.error(f"Error taking screenshot: {e.stderr.strip()}")
        notify(f"Error taking screenshot: {e.stderr.strip()}")
        sys.exit(1)
    except ValueError as e:
        logging.error(f"Error: {e}")
        notify(f"Error: {e}")
        sys.exit(1)

def upload_screenshot(data: bytes, api_key: str, domain: str) -> str:
    if not api_key or not domain:
        notify("Configuration incomplete. Please use the Go client to set up.")
        sys.exit(1)
    
    max_retries = 3
    base_timeout = 5

    logging.debug("Uploading screenshot...")
    print("Uploading", end="", flush=True)

    for attempt in range(max_retries):
        try:
            headers = {"key": api_key}
            files = {'file': ('screenshot.png', data, 'image/png')}
            
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
    if shutil.which('wl-copy'):
        subprocess.run(['wl-copy'], input=text.encode())
    elif shutil.which('xclip'):
        subprocess.run(['xclip', '-selection', 'clipboard'], input=text.encode())
    else:
        notify("Clipboard copy utility not found.")
        print("Clipboard copy utility not found.")

def mask_api_key(api_key: str) -> str:
    parts = api_key.split('_')
    if len(parts) > 1:
        return parts[0] + '_' + '*' * (len(parts[1]) - 3) + parts[1][-3:]
    return api_key

def add_text_to_image(image_data, top_text="", bottom_text="", color="white", font_path="~/.config/e-zshot/impact.ttf"):
    image = Image.open(io.BytesIO(image_data))
    draw = ImageDraw.Draw(image)

    # Increase base font size for more prominent text
    base_font_size = int(image.height / 8)  # Increase base size for larger text
    max_font_size = int(image.height / 3)    # Larger maximum size to handle lower resolutions better

    font_path = os.path.expanduser(font_path)  # Expand user directory in font path

    def get_font(size):
        try:
            return ImageFont.truetype(font_path, size)
        except IOError:
            return ImageFont.load_default().font_variant(size=size)

    def calculate_text_size(text, font):
        bbox = draw.textbbox((0, 0), text, font=font)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]

    def draw_text_with_outline(text, position, font):
        text_width, text_height = calculate_text_size(text, font)
        x, y = position
        # Draw the text with an outline
        for offset in [(1,1), (-1,-1), (1,-1), (-1,1)]:
            draw.text((x + offset[0], y + offset[1]), text, font=font, fill="black")
        draw.text((x, y), text, font=font, fill=color)

    # Adjust font size dynamically for top and bottom text
    font_size = base_font_size
    while True:
        font = get_font(font_size)
        text_width_top, _ = calculate_text_size(top_text, font) if top_text else (0, 0)
        text_width_bottom, _ = calculate_text_size(bottom_text, font) if bottom_text else (0, 0)
        if (text_width_top < image.width - 40 and text_width_bottom < image.width - 40) or font_size >= max_font_size:
            break
        font_size += 2  # Increase increment for faster scaling

    # Draw the top text
    if top_text:
        font = get_font(font_size)
        text_width, text_height = calculate_text_size(top_text, font)
        position = ((image.width - text_width) / 2, 10)
        draw_text_with_outline(top_text, position, font)

    # Draw the bottom text with extra padding to avoid cutting off
    if bottom_text:
        font = get_font(font_size)
        text_width, text_height = calculate_text_size(bottom_text, font)
        position = ((image.width - text_width) / 2, image.height - text_height - 20)  # Increased padding from bottom
        draw_text_with_outline(bottom_text, position, font)

    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()

def parse_color(color_str):
    if color_str.lower() in ['red', 'green', 'blue', 'white', 'black', 'yellow']:
        return color_str.lower()
    elif color_str.startswith('#'):
        return color_str
    elif ',' in color_str:
        values = [int(x.strip()) for x in color_str.split(',')]
        if len(values) == 3:
            return f"rgb({values[0]}, {values[1]}, {values[2]})"
        elif len(values) == 4:
            return f"rgba({values[0]}, {values[1]}, {values[2]}, {values[3]})"
    return "white"

def save_screenshot(data: bytes, save_path: str) -> None:
    if os.path.isdir(save_path):
        filename = f"{uuid.uuid4().hex[:8]}.png"
        full_path = os.path.join(save_path, filename)
    else:
        full_path = save_path
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
    
    with open(full_path, 'wb') as f:
        f.write(data)
    logging.debug(f"Screenshot saved to {full_path}")
    notify(f"Screenshot saved to {full_path}")

def download_font_if_missing(font_path: str, font_url: str) -> None:
    if not os.path.exists(font_path):
        logging.info(f"Font file not found at {font_path}. Downloading...")
        try:
            response = requests.get(font_url, timeout=10)
            response.raise_for_status()
            with open(font_path, 'wb') as f:
                f.write(response.content)
            logging.info(f"Font downloaded and saved to {font_path}.")
        except requests.RequestException as e:
            logging.error(f"Failed to download font: {e}")
            notify(f"Failed to download font: {e}")
            sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Screenshot tool that uploads to an external server.")
    parser.add_argument('-v', '--verbose', action='store_true', help="Enable verbose logging")
    parser.add_argument('-f', '--full-screen', action='store_true', help="Take a full-screen screenshot")
    parser.add_argument('-s', '--save-to-disk', type=str, help="Save the screenshot to the specified path")
    parser.add_argument('-n', '--no-upload', action='store_true', help="Disable uploading the screenshot to API")
    parser.add_argument('-t', '--top-text', type=str, help="Text to add at the top of the image")
    parser.add_argument('-b', '--bottom-text', type=str, help="Text to add at the bottom of the image")
    parser.add_argument('-c', '--color', type=str, default="white", help="Text color (name, hex, or RGB/RGBA)")
    parser.add_argument('-fpath', '--font-path', type=str, default=os.path.expanduser('~/.config/e-zshot/impact.ttf'),
                        help="Path to the font file (default: ~/.config/e-zshot/impact.ttf)")

    args = parser.parse_args()

    configure_logging(args.verbose)
    
    config = load_config()
    api_key = config['api_key']
    domain = config['domain']

    # Define the default font path and URL
    default_font_path = os.path.expanduser('~/.config/e-zshot/impact.ttf')
    font_url = 'https://raw.githubusercontent.com/sophilabs/macgifer/master/static/font/impact.ttf'

    # Download the font if it's not available
    download_font_if_missing(default_font_path, font_url)

    # Use the specified or default font path
    font_path = args.font_path if os.path.isfile(args.font_path) else default_font_path
    
    screenshot_data = take_screenshot(args.full_screen)

    if args.top_text or args.bottom_text:
        color = parse_color(args.color)
        screenshot_data = add_text_to_image(screenshot_data, args.top_text, args.bottom_text, color, font_path)

    if args.save_to_disk:
        save_screenshot(screenshot_data, args.save_to_disk)
    
    if not args.no_upload:
        start_time = time.time()
        image_url = upload_screenshot(screenshot_data, api_key, domain)
        elapsed_time = time.time() - start_time
        
        if not image_url:
            notify("Error: Empty or null image URL.")
            sys.exit(1)

        final_url = f"{domain.rstrip('/')}/{image_url.split('/')[-1]}"
        copy_to_clipboard(final_url)
        masked_api_key = mask_api_key(api_key)
        
        print(f"Screenshot URL: {final_url} (took {elapsed_time:.2f}s)")
        if args.verbose:
            print(f"API Key: {masked_api_key}")
        
        notify(f"Screenshot uploaded. URL: {final_url}")
    else:
        logging.debug("Screenshot not uploaded.")

if __name__ == "__main__":
    main()
