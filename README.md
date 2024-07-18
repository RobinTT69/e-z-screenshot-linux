# Dependencies

- Python
- flameshot - for takimg screenshots (primary)
- grim - for taking screenshots (if flameshot is broken)
- slurp - for selecting screen areas
- requests - for making HTTP requests
- xclip - for managing clipboard content on x11 systems

## Install requests with pip
```bash
pip install requests
```

### For other dependencies:

**On Arch Based Systems**
```bash
sudo pacman -S grim jq slurp xclip flameshot
```

**On Debian/Ubuntu based systems**
```bash
sudo apt install grim jq slurp xclip flameshot
```

**On Fedora based systems**
```bash
sudo dnf install grim jq slurp xclip flameshot
```

**On Gentoo systems**
```bash
sudo emerge -av gui-apps/grim gui-apps/slurp app-misc/jq xclip flameshot
```

# Usage

To use this script, follow these steps:

```bash
git clone https://github.com/RobinTT69/e-z-screenshot-linux
cd e-z-screenshot-linux
```
Now, assuming you have installed python as mentioned earlier, you can run the script by:

```bash
chmod +x e-z-flameshot.py
./e-z-flameshot.py
```
Or of you are using the grim script (if flameshot does not work)

```bash
chmod +x e-z-grim.py
./e-z-grim.py
```

# OPTIONS:
- -a, --api-key: Enter API key (required once, unless updating)
- -d, --domain: Enter the domain to be used (setup required, omit if not applicable)
- -s, --save-dir: Directory to save the screenshot
- -f, --full-screen: Capture full screen instead of a selected area
- -v, --verbose: Enable verbose logging for debugging 
- --top-text: Text to display at the top of the screenshot
- --bottom-text: Text to display at the bottom of the screenshot
- --use-frame: Use a black frame around the text (only if text is provided)

# Locating your API key

- Go to Account Settings

![image](https://i.e-z.host/pics/m9j6jk3a.png)

- Click 'Copy API Key'

![image](https://i.e-z.host/pics/inmghmtw.png)

# Using your own custom domain

You can use a subdomain for the image host instead of your whole domain:

- ### Step 1: Domain Setup On Cloudflare 

![image](https://r2.e-z.host/ca19848c-de8c-4cae-9a10-858d6fd864b7/joyc6m3h.jpeg)

Set up a DNS record for your subdomain:

![image](https://r2.e-z.host/8a13052f-8c12-4034-b99f-0155cc616583/f5jrvtyn.png)

- ### Step 2: Add Domain With Script Argument

Run `./SCRIPT-NAME.py -d https://cdn.yourdomain.com/`

# Troubleshooting

- **The python script doesn't work! It doesn't embed the images!** 

Ensure "Preserve query string" is enabled in Cloudflare and purge all caches.

- **I need to change my domain or API key!**

Run the script with `-a` and `-d` arguments as you did initially.

# Credits

Credits to [KeiranScript](https://github.com/KeiranScript) for contributing and adding custom domain functionality.
