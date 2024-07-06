# Dependencies
The dependencies for this script are `grim`, `jq` and `slurp`. To install:

**On Arch:** `sudo pacman -S grim jq slurp`

**On Debian/Ubuntu based systems** `sudo apt-get update` and then
`sudo apt-get install grim jq slurp`

**On Fedora based systems** `sudo dnf install grim jq slurp`

# Usage

In order to use this script, type the following commands into the terminal:

`$ git clone https://github.com/6942690/e-z-screenshot-grim-linux`

`$ cd e-z-screenshot-grim-linux`

`$ chmod +x e-z.sh`

Finally, using your favourite text editor, replace `'{YOUR-API-KEY}'` in
`e-z.sh` with your e-z host api key, as demonstrated below:

## Go to Account Settings

![image](https://github.com/KeiranScript/e-z-grim/assets/159267417/284186ed-7c76-4892-aeed-c27178b6f90f)

## Click 'Copy API Key'

![image](https://github.com/KeiranScript/e-z-grim/assets/159267417/8c62ae8d-171a-4a7d-b723-2ac92d031b80)

Now paste that API key into the script and you should be good to go. 

# Bind script to keyboard shortcut on Hyprland (Optional)

If you plan on using this on Hyprland, and want to bind it to a keyboard shortcut do the following:

## Open up hyprland.conf 

Open up `~/.config/hypr/hyprland.conf` with your favourite text editor.

## Add the bind

Add `bind = ,code:82, exec, sh ~/PATH-TO-SCRIPT &` to the file. Replace the `,code:82` with your desired [key](https://wiki.hyprland.org/Configuring/Binds/), and make sure to specify the path to script.

![image](https://i.e-z.host/fyp7qsmt.png)

# Disclaimer

This script was designed with wayland in mind, so if you are running x11, look into using the flameshot alternative for this made by [SKRRRTT](https://github.com/ignSKRRRTT/e-z-flameshot-script).

# Credits 
Credits to https://github.com/KeiranScript for helping me make this amazing readme!
