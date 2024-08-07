## Dependencies test
*Dependencies are automatically installed by your AUR Helper on Arch Linux.*

- Python
- Python-requests
- xclip
- Flameshot (Optional, but recommended)
- Grim (Optional if Flameshot is installed)
- Slurp (If using grim)
- Slop (If using X11 without Flameshot)

#### Depending on your operating system, you may need to install the requests module for python differently.

With PIP
```sh
pip install requests
```
or
```sh
pip3 install requests
```

With Pacman
```sh
sudo pacman -S python-requests
```

### Dependencies

Arch Linux Based Systems
```sh
sudo pacman -S grim jq slurp xclip flameshot slop
```

Debian/Ubuntu Based Systems
```sh
sudo apt install grim jq slurp xclip flameshot slop
```

Fedora Based Systems
```sh
sudo dnf install grim jq slurp xclip flameshot slop
```

Gentoo Based Systems
```sh
sudo emerge -av gui-apps/grim gui-apps/slurp app-misc/jq xclip flameshot slop
```

<details>
<summary>Arch installation via the AUR</summary>

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

If installed via AUR, enter the command
```sh
e-zconfig
```

and follow the interactive prompts.

Otherwise
```bash
cd e-z-screenshot-linux
./e-zconfig.sh
```

**e-zshot is now done being configured, and you can run it**

```bash
./e-zshot.py
```

**By default, e-zshot is not installed to your binaries directory. You can do this manually at your own risk, but we do not recommend it if you don't know what you're doing.**

## Arguments

- `-h, --help`: List all options and usage
- `-s, --save-to-disk`:  Save the screenshot to the specified path
- `-f, --full-screen`: Capture full screen instead of a selected area
- `-v, --verbose`: Enable verbose logging for debugging 
- `-t, --top-text`: Text to display at the top of the screenshot (e.g. `-t 'Hello'`)
- `-b, --bottom-text`: Text to display at the bottom of the screenshot (e.g. `-b 'World!'`)
- `-c, --colour`: Choose text colour (e.g. `-c black` or `-c #000000`)

## Understanding your configuration

#### You may have gotten a little curious and taken a look at your `config.json` file, only to be confused. Don't worry, we'll break it down for you!

config.json
```json
{
	"api_key": "your-api-key",
	"domain": "your-domain.gg",
	"image_type": "png",
	"compression_level": "4",
	"save_to_disk": "",
	"upload_to_api": "",
	"verbose": "",
	"screenshot_tool": "flameshot"
  }
```

- API Key - Self explanatory. Refer to the section below if unsure.
- Domain - The domain you would like your screenshot to be linked to.
- Image Type - Also fairly self explanatory. JPG/PNG/Webp
- Compression Level - When using Grim with PNGs, it applies a certain amount of compression. This can be either disabled, lowered or increased by changing this value. Values 0-9 are acceptable.
- Save To Disk - Saves your screenshot to your device. Defaults to ~/Pictures/Screenshots but can be edited.
- Verbose - Enables verbose output, useful for diagnosing issues with the program. Don't use this unless you have problems.
- Screenshot Tool - Which program you'd like to use in order to capture screenshots. Flameshot, Grim and Gnome-Screenshot.

If you have any more questions, contact <a href="https://discord.com/users/1230319937155760131" target="__blank">keirandev</a> or <a href="https://discord.com/users/685666840021958685" target="__blank">RobinTT</a> on Discord.
## Locating your API Key

- Go to Account Settings

	![Account Settings](https://i.e-z.host/pics/m9j6jk3a.png)

- Click 'Copy API Key'

	![Copy API Key](https://i.e-z.host/pics/inmghmtw.png)

## Using your own custom domain (optional)

**Replace "cdn" with your desired subdomain:**

### Domain Setup On Cloudflare (Redirect Rule)

![Redirect Rule](https://r2.e-z.host/8a13052f-8c12-4034-b99f-0155cc616583/vbzqydsx.png)

Set up a DNS record for your subdomain:

![DNS Record](https://r2.e-z.host/8a13052f-8c12-4034-b99f-0155cc616583/f5jrvtyn.png)

## Troubleshooting

- **It doesn't embed the images!**

  Ensure "Preserve query string" is enabled in Cloudflare and purge all caches.

- **I need to change my domain or API key!**

  Run `e-zconfig` with your updated credentials or domain..

## Credits

Credits to [KeiranScript](https://github.com/KeiranScript) for contributing and adding custom domain functionality.

### Oliver

<img src="https://r2.e-z.host/oliver.png" alt="oliver" width="128" height="128">
