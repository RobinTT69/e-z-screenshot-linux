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
        file_path = os.path.join(directory, file_name)  # Append .jpeg here
        with open(file_path, 'wb') as file:
            file.write(data)
        print(f"Screenshot saved to {file_path}")
    except Exception as e:
        print(f"Error saving screenshot: {e}")
        exit(1)

def take_screenshot_and_upload(api_key, config, args):
    try:
        # Take screenshot using Flameshot
        temp_file = "/tmp/screenshot.png"
        subprocess.run(['flameshot', 'gui', '-r', '-p', temp_file], check=True)

        # Check if the file is a valid image
        if subprocess.run(['file', '--mime-type', '-b', temp_file], capture_output=True, text=True).stdout.strip() != "image/png":
            print("Invalid file type or error in screenshot")
            exit(1)

        # Upload the screenshot using API
        url = "https://api.e-z.host/files"
        files = {"file": ("screenshot.png", open(temp_file, 'rb'), "image/png")}
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

        # Copy URL to clipboard (X11 compatible)
        final_url = config['domain'] + unique_id
        copy_to_clipboard_x11(final_url)

        # Save to disk if directory is specified
        save_dir = args.save_dir
        if save_dir:
            if os.path.isdir(save_dir) and os.access(save_dir, os.W_OK):
                save_to_disk(save_dir, unique_id, open(temp_file, 'rb').read())  # Save without additional .jpeg
            else:
                print("Invalid directory or permission denied.")
                exit(1)

        print(f"Screenshot URL: {final_url}")

        # Send notification that URL has been copied (X11 compatible)
        send_notification_x11("URL copied!", f"URL: {final_url}")

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

def copy_to_clipboard_x11(text):
    try:
        subprocess.run(['xclip', '-selection', 'clipboard'], input=text.encode())
    except Exception as e:
        print(f"Error copying to clipboard: {e}")

def send_notification_x11(title, message):
    try:
        subprocess.run(['notify-send', title, message])
    except Exception as e:
        print(f"Error sending notification: {e}")

def main():
    config_path = get_config_path()
    ensure_config_file_exists(config_path)
    config = load_config()

    parser = argparse.ArgumentParser(description="Screenshot tool that uploads to an external server.")
    parser.add_argument('-A', '--api-key', type=str, help="Enter API key")
    parser.add_argument('-D', '--domain', type=str, help="Enter the domain to be used")
    parser.add_argument('-S', '--save-dir', type=str, help="Directory to save screenshot")

    args = parser.parse_args()

    if args.api_key:
        enter_api_key(args.api_key, config)

    if args.domain:
        enter_domain(args.domain, config)

    api_key = config.get('api_key')

    if not api_key:
        parser.print_help()
        send_notification_x11("API Key Missing", "Please provide an API key using the '-A' option.")
        exit(1)

    # Set the domain URL
    config['domain'] = config.get('domain', "https://i.e-z.host/")  # Default to "https://i.e-z.host/" if domain is not set

    take_screenshot_and_upload(api_key, config, args)

if __name__ == "__main__":
    main()
