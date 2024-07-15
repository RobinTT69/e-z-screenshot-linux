#!/bin/sh

APIKEY="Keiran_cyrdkchl1ohewu15gi316btqxt18vt"
# Check that API key exists.
if [ "$APIKEY" = "null" ]; then
  notify-send "Please replace the 'APIKEY' variable with your API key as demonstrated in the git repo's readme."
  echo "Please replace the 'APIKEY' variable with your API key as demonstrated in the git repo's readme."
  exit 0
fi

#Take the screeshot from selected area
response=$(grim -g "$(slurp)" -t jpeg - | curl -sS -X POST -H "key: $APIKEY" -F "file=@-" https://api.e-z.host/files)

#Error checking for upload error.
if [ -z "$response" ]; then
    echo "Error: Upload failed or response is empty."
    notify-send "Error" "Upload failed or response is empty."
    exit 1
fi

#Copy Uploaded URL
imageUrl=$(echo "$response" | jq -r '.imageUrl')

#Error check for the case that image was never taken, resulting in null from grim.
if [ "$imageUrl" = "null" ] || [ -z "$imageUrl" ]; then
    echo "Error: Image URL is empty or null."
    notify-send "Error" "Image URL is empty or null."
    exit 1
fi

#URL pasted to console.
echo "$imageUrl" | wl-copy

#Notification
notify-send "Screenshot uploaded" "URL copied to clipboard: $imageUrl"

exit 0
