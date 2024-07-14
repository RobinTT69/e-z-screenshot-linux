# Dependencies
The dependencies for this script are `grim`, `jq` and `slurp`. To install:

**On Arch:** `sudo pacman -S grim jq slurp`

**On Debian/Ubuntu based systems** `sudo apt update` and then
`sudo apt install grim jq slurp`

**On Fedora based systems** `sudo dnf install grim jq slurp`

**On Gentoo systems** `sudo emerge -av gui-apps/grim gui-apps/slurp app-misc/jq`

**On Windows systems** `Install Linux`

# Usage

In order to use this script, enter the following commands into the terminal:

`$ git clone https://github.com/RobinTT69/e-z-screenshot-grim-linux`

`$ cd e-z-screenshot-grim-linux`

Then, using your favourite text editor, replace the `APIKEY` variable in
`e-z.sh` with your e-z host api key, as demonstrated below:

- Go to Account Settings

![image](https://i.e-z.host/pics/m9j6jk3a.png)

- Click 'Copy API Key'

![image](https://i.e-z.host/pics/inmghmtw.png)

Now paste that API key into the script and you should be good to go. 

## **If you plan on using this on Hyprland, and want to bind it to a keyboard shortcut do the following:**

  - Open up `~/.config/hypr/hyprland.conf` with your favourite text editor.
  - Add `bind = ,code:82, exec, sh ~/PATH-TO-SCRIPT &` to the file. Replace the `,code:82` with your desired [key](https://wiki.hyprland.org/Configuring/Binds/), and make sure to specify the path to script.
  
    ![image](https://i.e-z.host/fyp7qsmt.png)

# Using your own custom domain (For Advanced Users)

If you are interested in using a custom domain, but are not interested in changing nameservers to the E-Z ones, do the following: 

- Download Python
- Download the e-z.py file in this repo
- Run the Script with the arguements -A and -D. Right after -A but your api key and after -D put the domain. You only have to do this on the first time you run the script as the script saves the config to your disk.
### Make Sure To Type The Domain In The https://sub.domain.tld/ Format!

## Domain Setup On Cloudflare (enter this subdomain that you have set up when the script asks for it)
![image](https://r2.e-z.host/ca19848c-de8c-4cae-9a10-858d6fd864b7/joyc6m3h.jpeg)

You have to also make a dns record

![image](https://r2.e-z.host/8a13052f-8c12-4034-b99f-0155cc616583/f5jrvtyn.png)

Make sure its the subdomain you want, as well as making it point to 192.0.0.2

### Troubleshooting
- **The python script doesnt work! It doesnt embed the images!** 
To fix this go back to the cloudflare rule you made. Tick the box that says "Preserve query string". Also, purge all cache if you have any. Now try the embed.

- **I need to change my domain! I need to change my api key!**
Run the script and this time add the -A and -D arguements, just like you did the first time you used the script.

# Disclaimer

This script was designed with wayland in mind, so if you are running x11, look into using the flameshot alternative for this made by [SKRRRTT](https://github.com/ignSKRRRTT/e-z-flameshot-script).

# Credits
Credits and huge thanks to https://github.com/KeiranScript for being a contributor who helps me maintain this project as well as adding the python script for the custom domain option.
