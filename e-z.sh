#!/bin/sh

response=$(grim -g "$(slurp)" -t jpeg - | curl -sS -X POST -H "key: {YOUR-API-KEY}" -F "file=@-" https://api.e-z.host/files)


if [ -z "$response" ]; then
    echo "Error: Upload failed or response is empty."
    notify-send "Error" "Upload failed or response is empty."
    exit 1
fi


imageUrl=$(echo "$response" | jq -r '.imageUrl')

if [ "$imageUrl" = "null" ] || [ -z "$imageUrl" ]; then
    echo "Error: Image URL is empty or null."
    notify-send "Info:" "Image URL is empty or null."
    exit 1
fi


echo "$imageUrl" | wl-copy

notify-send "Screenshot uploaded" "URL copied to clipboard: $imageUrl"

exit 0
