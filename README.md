
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
<details>
<summary>On Arch based systems using the AUR</summary>

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
</details>

<details>
<summary>For non-arch distros</summary>

```bash
git clone https://github.com/RobinTT69/e-z-screenshot-linux
cd e-z-screenshot-linux
chmod +x ./e-zconfig.sh
chmod +x ./e-zshot.py
```
</details>

## Configuration and usage

**If you downloaded e-zshot from the aur, run `e-zconfig` and follow the onscreen prompts. Other wise:**

```bash
cd e-z-screenshot-linux
./e-zconfig.sh
```
**e-zshot is now done being configured, and you can run it.** 

```bash
e-zshot
```

## Arguments

- `-h, --help`: List all options and usage
- `-s, --save-to-disk`:  Save the screenshot to the specified path
- `-f, --full-screen`: Capture full screen instead of a selected area
- `-v, --verbose`: Enable verbose logging for debugging 
- `-t, --top-text`: Text to display at the top of the screenshot (e.g. `-t 'Hello'`)
- `-b, --bottom-text`: Text to display at the bottom of the screenshot (e.g. `-b 'World!'`)
- `-c, --colour`: Choose text colour (e.g. `-c black` or `-c #000000`)

## Locating your API key

- Go to Account Settings

![Account Settings](https://i.e-z.host/pics/m9j6jk3a.png)

- Click 'Copy API Key'

![Copy API Key](https://i.e-z.host/pics/inmghmtw.png)

Now run:
```bash
e-zconfig
```

## Using your own custom domain (optional)

**Replace "cdn" with your desired subdomain:**

### Step 1: Domain Setup On Cloudflare (Redirect Rule)

![Redirect Rule](https://r2.e-z.host/8a13052f-8c12-4034-b99f-0155cc616583/vbzqydsx.png)

Set up a DNS record for your subdomain:

![DNS Record](https://r2.e-z.host/8a13052f-8c12-4034-b99f-0155cc616583/f5jrvtyn.png)

### Step 2: Add Domain Using Config 

Run:
```bash
e-zconfig
```

## Troubleshooting

- **It doesn't embed the images!**

  Ensure "Preserve query string" is enabled in Cloudflare and purge all caches.

- **I need to change my domain or API key!**

  Run `e-zconfig` with your updated credentials or domain..

## Credits

Credits to [KeiranScript](https://github.com/KeiranScript) for contributing and adding custom domain functionality.

### Oliver

<img src="https://r2.e-z.host/oliver.png" alt="oliver" width="128" height="128">
