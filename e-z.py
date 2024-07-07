#!/usr/bin/python3

import subprocess
import requests
import json
import os

APIKEY = "null" # Your API key here

NEW_BASE_URL = "https://example.com" # Your domain here (It MUST redirect to a domain owned by e-z.gg)

# Check that API key exists.
if APIKEY == "null":
    subprocess.run(['notify-send', "Please replace the 'APIKEY' variable with your API key as demonstrated in the git repo's readme."])
    print("Please replace the 'APIKEY' variable with your API key as demonstrated in the git repo's readme.")
    exit(0)

# Take the screenshot from selected area
try:
    # Get the selected area using slurp
    slurp_result = subprocess.run(['slurp'], capture_output=True, text=True, check=True)
    geometry = slurp_result.stdout.strip()
    
    if not geometry:
        raise ValueError("No area selected")

    # Take the screenshot using grim
    grim_result = subprocess.run(['grim', '-g', geometry, '-t', 'jpeg', '-'], capture_output=True, check=True)
    screenshot_data = grim_result.stdout
except subprocess.CalledProcessError as e:
    print(f"Error taking screenshot: {e}")
    exit(1)
except ValueError as e:
    print(e)
    exit(1)

# Upload the screenshot
try:
    response = requests.post(
        "https://api.e-z.host/files",
        headers={"key": APIKEY},
        files={"file": ("screenshot.jpeg", screenshot_data, "image/jpeg")}
    )
    response.raise_for_status()
    response_json = response.json()
except requests.RequestException as e:
    print(f"Error uploading screenshot: {e}")
    subprocess.run(['notify-send', "Error", f"Error uploading screenshot: {e}"])
    exit(1)

# Copy Uploaded URL
imageUrl = response_json.get('imageUrl')

# Error check for the case that image was never taken, resulting in null from grim.
if not imageUrl or imageUrl == "null":
    print("Error: Image URL is empty or null.")
    subprocess.run(['notify-send', "Error", "Image URL is empty or null."])
    exit(1)

# Replace the base URL with the new one
new_image_url = NEW_BASE_URL + imageUrl.split('/')[-1]

# URL pasted to console.
subprocess.run(['wl-copy'], input=new_image_url.encode())

# Notification
subprocess.run(['notify-send', "Screenshot uploaded", f"URL: {new_image_url}"])

exit(0)
