import argparse
import subprocess
import sys
import importlib
import os
import requests
from config import ensure_config_file_exists, load_config, save_config
from screenshot import take_screenshot, handle_error, upload_screenshot

PLUGIN_DIR = os.path.expanduser('~/.config/e-zshot/plugins')

def install_plugins(plugin_names, repo_url):
    os.makedirs(PLUGIN_DIR, exist_ok=True)
    for plugin_name in plugin_names:
        plugin_path = os.path.join(PLUGIN_DIR, f"{plugin_name}.py")
        if not os.path.exists(plugin_path):
            print(f"Installing plugin {plugin_name} from {repo_url}")
            plugin_url = f"{repo_url}/{plugin_name}.py"
            try:
                response = requests.get(plugin_url)
                response.raise_for_status()
                with open(plugin_path, 'w') as f:
                    f.write(response.text)
            except requests.RequestException as e:
                print(f"Failed to download plugin {plugin_name}: {e}")

def load_plugins(config):
    plugins = {}
    repo_url = config.get('plugin_repo_url')
    if repo_url:
        install_plugins(config.get('plugins', []), repo_url)
    for plugin in config.get('plugins', []):
        try:
            sys.path.append(PLUGIN_DIR)
            plugins[plugin] = importlib.import_module(plugin)
        except ImportError as e:
            print(f"Failed to load plugin {plugin}: {e}")
    return plugins

def main():
    parser = argparse.ArgumentParser(description="Screenshot tool that uploads to E-Z Hosting API.")
    parser.add_argument('-a', '--api-key', type=str, help="API key")
    parser.add_argument('-d', '--domain', type=str, help="Domain to use")
    parser.add_argument('-s', '--save-dir', type=str, help="Directory to save screenshot")
    parser.add_argument('-f', '--full-screen', action='store_true', help="Capture full screen")
    parser.add_argument('-v', '--verbose', action='store_true', help="Show more info")
    parser.add_argument('-t', '--top-text', type=str, help="Text at the top of the screenshot")
    parser.add_argument('-b', '--bottom-text', type=str, help="Text at the bottom of the screenshot")
    parser.add_argument('-c', '--colour', type=str, default='white', help="Text color")
    parser.add_argument('-ft', '--file-type', type=str, choices=['PNG'], default='PNG', help="File type to save (PNG only)")
    parser.add_argument('-cl', '--compression-level', type=int, default=6, help="Compression level for PNG (0-9)")
    
    args = parser.parse_args()
    verbose = args.verbose
    
    ensure_config_file_exists(CONFIG_FILE, verbose)
    config = load_config()
    
    config.update({
        'file_type': args.file_type,
        'compression_level': args.compression_level
    })
    
    if args.api_key:
        config['api_key'] = args.api_key
    if args.domain:
        config['domain'] = args.domain
    
    save_config(config)

    plugins = load_plugins(config)
    
    if 'logging_plugin' in plugins:
        plugins['logging_plugin'].setup_logging()
    
    api_key = config.get('api_key')
    if not api_key:
        parser.print_help()
        handle_error("API key is missing. Use '-a' option.")
    
    domain = config.get('domain', "https://i.e-z.host/")
    
    if 'gui_plugin' in plugins:
        args.top_text, args.bottom_text = plugins['gui_plugin'].prompt_text_input()
    
    screenshot_data = take_screenshot(args.full_screen, verbose)
    
    if 'text_processing_plugin' in plugins:
        screenshot_data = plugins['text_processing_plugin'].add_text_to_image(
            screenshot_data, args.top_text, args.bottom_text, args.colour, config['file_type'], config['compression_level']
        )

    image_url = upload_screenshot(screenshot_data, api_key, verbose)
    if not image_url or image_url == "null":
        handle_error("Empty or null image URL.")
    
    unique_id = image_url.split('/')[-1]
    
    if args.save_dir:
        if os.path.isdir(args.save_dir) and os.access(args.save_dir, os.W_OK):
            save_to_disk(args.save_dir, unique_id, screenshot_data, config['file_type'])
        else:
            handle_error("Invalid directory or no write permissions.")
    
    new_image_url = domain + unique_id
    subprocess.run(['wl-copy'], input=new_image_url.encode())
    subprocess.run(['notify-send', "Screenshot uploaded", f"URL: {new_image_url}"])
    
    if 'logging_plugin' in plugins:
        plugins['logging_plugin'].log_message(f"Screenshot URL: {new_image_url}")

if __name__ == "__main__":
    main()
