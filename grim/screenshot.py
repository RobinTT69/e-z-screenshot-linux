import io
import os
import subprocess
from PIL import ImageGrab

def handle_error(message: str) -> None:
    print(f"Error: {message}")
    exit(1)

def take_screenshot(full_screen: bool, verbose: bool) -> bytes:
    try:
        if full_screen:
            if verbose:
                print("Taking full screen screenshot")
            screenshot = ImageGrab.grab()
        else:
            if verbose:
                print("Taking screenshot of selected area")
            screenshot = ImageGrab.grabclipboard()
        
        if not screenshot:
            handle_error("Failed to take screenshot. Make sure you have an area selected if not using full screen.")
        
        with io.BytesIO() as output:
            screenshot.save(output, format="PNG")
            return output.getvalue()
    except Exception as e:
        handle_error(f"Error taking screenshot: {e}")

def upload_screenshot(screenshot_data: bytes, api_key: str, verbose: bool) -> str:
    import requests
    try:
        if verbose:
            print("Uploading screenshot")
        
        response = requests.post(
            'https://api.e-z.host/upload',
            headers={'Authorization': f'Bearer {api_key}'},
            files={'file': ('screenshot.png', io.BytesIO(screenshot_data), 'image/png')}
        )
        
        if response.status_code == 200:
            return response.json().get('url')
        else:
            handle_error(f"Failed to upload screenshot. Status code: {response.status_code}, Response: {response.text}")
    except Exception as e:
        handle_error(f"Error uploading screenshot: {e}")

def save_to_disk(directory: str, filename: str, data: bytes, file_type: str) -> None:
    try:
        path = os.path.join(directory, f"{filename}.{file_type.lower()}")
        with open(path, 'wb') as f:
            f.write(data)
        print(f"Screenshot saved to {path}")
    except Exception as e:
        handle_error(f"Error saving screenshot to disk: {e}")
