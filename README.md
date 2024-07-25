
# e-zshot

## Dependencies

*Note: Dependencies are automatically installed when building via the AUR*

- **Python** - for running the script
- **Flameshot** - for taking screenshots (primary screenshot tool)
- **Grim** - for taking screenshots (secondary screenshot tool if flameshot is broken)
- **Slurp** - for selecting screen areas
- **Slop** - for selecting screen areas (x11)
- **python-requests** - for making HTTP requests
- **xclip** - for managing clipboard content on x11 systems

### Install `requests` with pip
*(Python should be installed prior to this)*
```bash
pip install requests
```

### For other dependencies:

**On Arch Based Systems:**
```bash
sudo pacman -S grim jq slurp xclip flameshot python-requests slop
```

**On Debian/Ubuntu based systems:**
```bash
sudo apt install grim jq slurp xclip flameshot slop
```

**On Fedora based systems:**
```bash
sudo dnf install grim jq slurp xclip flameshot slop
```

**On Gentoo systems:**
```bash
sudo emerge -av gui-apps/grim gui-apps/slurp app-misc/jq xclip flameshot slop
```

## Installation

### On Arch based systems using the AUR

#### Paru
```bash
paru -S e-zshot
```

#### Yay
```bash
yay -S e-zshot
```

#### Clone with git and build manually
```bash
git clone https://aur.archlinux.org/e-zshot.git
cd e-zshot
makepkg -si
cd ..
rm -rf e-zshot
```

### For non-arch distros

```bash
git clone https://github.com/RobinTT69/e-z-screenshot-linux
cd e-z-screenshot-linux
```
COMING SOON

## Options

- `-h, --help`: List all options and usage
- `-a, --api-key`: Enter API key (required once, unless updating)
- `-d, --domain`: Enter the domain to be used (setup required, omit if not applicable)
- `-s, --save-dir`: Directory to save the screenshot
- `-f, --full-screen`: Capture full screen instead of a selected area
- `-v, --verbose`: Enable verbose logging for debugging 
- `-t, --top-text`: Text to display at the top of the screenshot (e.g. `-t 'Hello'`)
- `-b, --bottom-text`: Text to display at the bottom of the screenshot (e.g. `-b 'World!'`)
- `-g, --gui`: Launches PyQT dialog boxes to input text
- `-c, --colour`: Choose text colour (e.g. `-c black`)

## Locating your API key for the script

- Go to Account Settings

![Account Settings](https://i.e-z.host/pics/m9j6jk3a.png)

- Click 'Copy API Key'

![Copy API Key](https://i.e-z.host/pics/inmghmtw.png)

Now run:
```bash

```
You are now done with the script setup! Try it out, see if it works. If you want to use your own subdomain, follow the steps below. Otherwise, you are done!

## Using your own custom domain

Replace "cdn" with your desired subdomain:

### Step 1: Domain Setup On Cloudflare (Redirect Rule)

![Redirect Rule](https://r2.e-z.host/8a13052f-8c12-4034-b99f-0155cc616583/vbzqydsx.png)

Set up a DNS record for your subdomain:

![DNS Record](https://r2.e-z.host/8a13052f-8c12-4034-b99f-0155cc616583/f5jrvtyn.png)

### Step 2: Add Domain With Script Argument

Run:
```bash
./e-z-grim.py -d https://sub.yourdomain.com/
# or
e-z-grim -d https://sub.yourdomain.com/
```

## Troubleshooting

- **The python script doesn't work! It doesn't embed the images!**

  Ensure "Preserve query string" is enabled in Cloudflare and purge all caches.

- **I need to change my domain or API key!**

  Run the script with `-a` and `-d` arguments as you did initially.

## Credits

Credits to [KeiranScript](https://github.com/KeiranScript) for contributing and adding custom domain functionality.

### Oliver

<img src="https://r2.e-z.host/oliver.png" alt="oliver" width="128" height="128">
