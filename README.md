# Dependencies
The dependencies for this script are `grim`, `jq` and `slurp`. To install:

**On Arch:** `sudo pacman -S grim jq slurp`

**On Debian/Ubuntu based systems** `sudo apt update` and then
`sudo apt install grim jq slurp`

**On Fedora based systems** `sudo dnf install grim jq slurp`

**On Gentoo systems** `sudo emerge -av gui-apps/grim gui-apps/slurp app-misc/jq`

# Usage

In order to use this script, type the following commands into the terminal:

`$ git clone https://github.com/RobinTT69/e-z-screenshot-grim-linux`

`$ cd e-z-screenshot-grim-linux`

`$ chmod +x e-z.sh`

Finally, using your favourite text editor, replace the `APIKEY` variable in
`e-z.sh` with your e-z host api key, as demonstrated below:

## Go to Account Settings

![image](https://i.e-z.host/pics/m9j6jk3a.png)

## Click 'Copy API Key'

![image](https://i.e-z.host/pics/inmghmtw.png)

Now paste that API key into the script and you should be good to go. 

# **If you plan on using this on Hyprland, and want to bind it to a keyboard shortcut do the following:**

  - Open up `~/.config/hypr/hyprland.conf` with your favourite text editor.
  - Add `bind = ,code:82, exec, sh ~/PATH-TO-SCRIPT &` to the file. Replace the `,code:82` with your desired [key](https://wiki.hyprland.org/Configuring/Binds/), and make sure to specify the path to script.
  
    ![image](https://i.e-z.host/fyp7qsmt.png)


# Disclaimer

This script was designed with wayland in mind, so if you are running x11, look into using the flameshot alternative for this made by [SKRRRTT](https://github.com/ignSKRRRTT/e-z-flameshot-script).

# Credits 
Credits to https://github.com/KeiranScript for helping me make this amazing readme and adding additional checks to the script.
