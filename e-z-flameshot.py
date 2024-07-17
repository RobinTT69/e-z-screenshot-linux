#!/usr/bin/python3
import subprocess
import requests
import json
import os
import argparse
import sys
from PIL import Image, ImageDraw, ImageFont
import io

CONFIG_FILE = os.path.expanduser('~/.config/e-zshot/config.json')
FONT_PATH = os.path.join(os.path.dirname(__file__), 'fonts', 'impact.ttf')  # Local font path

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
    if domain:
        if not domain.startswith("https://"):
            print("Invalid domain. Please provide a valid domain starting with 'https://'.")
            exit(1)
        config['domain'] = domain
        save_config(config)
    else:
        config['domain'] = "https://i.e-z.host/"
        save_config(config)

def save_to_disk(directory, file_name, data):
    try:
        file_path = os.path.join(directory, file_name + ".png")  # Save as PNG
        with open(file_path, 'wb') as file:
            file.write(data)
        print(f"Screenshot saved to {file_path}")
    except Exception as e:
        print(f"Error saving screenshot: {e}")
        exit(1)

def add_text_to_image(image_data, top_text=None, bottom_text=None, use_frame=False):
    try:
        with Image.open(io.BytesIO(image_data)) as img:
            draw = ImageDraw.Draw(img)
            font = ImageFont.truetype(FONT_PATH, 40)

            # Function to draw text with optional frame
            def draw_text_with_frame(text, position, is_bottom):
                text_bbox = draw.textbbox((0, 0), text, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]

                # Centering
                text_x = (img.width - text_width) // 2
                text_y = position[1]

                if use_frame:
                    frame_position = (text_x - 10, text_y - (text_height // 2) - 10, text_x + text_width + 10,
                                      text_y + (text_height // 2) + 10)
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

    except Exception as e:
        print(f"Error adding text to image: {e}")
        exit(1)

def take_screenshot_and_upload(api_key, config, args):
    try:
        if args.fullscreen:
            subprocess.run(['flameshot', 'full', '-p', '/tmp/screenshot.png'], check=True)
        else:
            subprocess.run(['flameshot', 'gui', '-r', '-p', '/tmp/screenshot.png'], check=True)

        # Process the screenshot with text and frame
        temp_file = "/tmp/screenshot.png"
        with open(temp_file, 'rb') as f:
            screenshot_data = f.read()

        # Add text and frame to the screenshot
        screenshot_data = add_text_to_image(screenshot_data, args.top_text, args.bottom_text, args.use_frame)

        # Upload the screenshot using API
        url = "https://api.e-z.host/files"
        files = {"file": ("screenshot.png", screenshot_data, "image/png")}
        headers = {"key": api_key}

        response = requests.post(url, headers=headers, files=files)
        response.raise_for_status()
        response_json = response.json()
        image_url = response_json.get('imageUrl')

        if not image_url or image_url == "null":
            print("Error: Image URL is empty or null.")
            exit(1)

        # Extract unique ID from the URL
        unique_id = image_url.split('/')[-1]

        # Determine clipboard tool based on environment
        clipboard_tool = 'xclip'

        # Copy URL to clipboard using appropriate tool
        final_url = config['domain'] + unique_id
        subprocess.run([clipboard_tool, '-sel', 'c'], input=final_url.encode(), check=True)

        # Save to disk if directory is specified
        save_dir = args.save_dir
        if save_dir:
            if os.path.isdir(save_dir) and os.access(save_dir, os.W_OK):
                save_to_disk(save_dir, unique_id, screenshot_data)
            else:
                print("Invalid directory or permission denied.")
                exit(1)

        print(f"Screenshot URL: {final_url}")

    except subprocess.CalledProcessError as e:
        print(f"Error taking/uploading screenshot: {e}")
        exit(1)
    except requests.RequestException as e:
        print(f"Error uploading screenshot: {e}")
        exit(1)
    finally:
        # Clean up temporary file
        if os.path.exists(temp_file):
            os.remove(temp_file)

def send_notification(title, message):
    subprocess.run(['notify-send', title, message])

def main():
    config_path = get_config_path()
    ensure_config_file_exists(config_path)
    config = load_config()

    parser = argparse.ArgumentParser(description="Screenshot tool that uploads to an external server.")
    parser.add_argument('-a', '--api-key', type=str, help="Enter API key")
    parser.add_argument('-d', '--domain', type=str, help="Enter the domain to be used")
    parser.add_argument('-s', '--save-dir', type=str, help="Directory to save screenshot")
    parser.add_argument('-v', '--verbose', action='store_true', help="Enable verbose logging for debugging")
    parser.add_argument('-f', '--fullscreen', action='store_true', help="Capture a fullscreen screenshot")
    parser.add_argument('--top-text', type=str, help="Text to display at the top of the screenshot")
    parser.add_argument('--bottom-text', type=str, help="Text to display at the bottom of the screenshot")
    parser.add_argument('--use-frame', action='store_true', help="Use a black frame around the text (only if text is provided)")

    args = parser.parse_args()

    if args.api_key:
        enter_api_key(args.api_key, config)

    if args.domain:
        enter_domain(args.domain, config)

    api_key = config.get('api_key')

    if not api_key:
        parser.print_help()
        send_notification("API Key Missing", "Please provide an API key using the '-A' option.")
        exit(1)

    # Set the domain URL
    config['domain'] = config.get('domain', "https://i.e-z.host/")  # Default to "https://i.e-z.host/" if domain is not set

    take_screenshot_and_upload(api_key, config, args)

if __name__ == "__main__":
    main()
