# Dependencies
The dependencies for this script are `grim`, `jq` and `slurp` which can be installed by

**On Arch:** `sudo pacman -S grim jq slurp`

**On Debian/Ubuntu based systems** `sudo apt-get update` and then
`sudo apt-get install grim jq slurp`

**On Fedora based systems** `sudo dnf install grim jq slurp`

# Usage

In order to use this script, type the following commands into the terminal:

`$ git clone https://github.com/6942690/e-z-screenshot-grim-linux`

`$ cd e-z-screenshot-grim-linux`

`$ chmod +x e-z.sh`

Finally, using your favourite text editor, replace the `APIKEY` variable in
`e-z.sh` with your e-z host api key, as demonstrated below:

## Go to Account Settings

![image](https://github.com/KeiranScript/e-z-grim/assets/159267417/284186ed-7c76-4892-aeed-c27178b6f90f)

## Click 'Copy API Key'

![image](https://github.com/KeiranScript/e-z-grim/assets/159267417/8c62ae8d-171a-4a7d-b723-2ac92d031b80)

Now paste that API key into the script and you should be good to go. 

# Disclaimer

This script was designed with wayland in mind, so if you are running x11, look into using the flameshot alternative for this made by [SKRRRTT](https://github.com/ignSKRRRTT/e-z-flameshot-script).

# Credits 
Credits to https://github.com/KeiranScript for helping me make this amazing readme!
