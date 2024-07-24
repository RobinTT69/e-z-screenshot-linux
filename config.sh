#!/bin/bash

CONFIG_DIR="$HOME/.config/e-zshot"
CONFIG_FILE="$CONFIG_DIR/config.json"
DEFAULT_DOMAIN="https://i.e-z.host/"
DEFAULT_IMAGE_TYPE="png"
DEFAULT_COMPRESSION_LEVEL=6
DEFAULT_SCREENSHOT_TOOL="flameshot"

# Function to prompt user for input with a default value
prompt_user() {
    local question=$1
    local default_value=$2
    read -p "$question [$default_value]: " input
    echo "${input:-$default_value}"
}

# Function to prompt user for integer input with a default value
prompt_int() {
    local question=$1
    local default_value=$2
    local input
    input=$(prompt_user "$question" "$default_value")
    if [[ ! $input =~ ^[0-9]+$ ]]; then
        echo "$default_value"
    else
        echo "$input"
    fi
}

# Function to prompt user for boolean input with a default value
prompt_bool() {
    local question=$1
    local default_value=$2
    local default_str="n"
    [[ $default_value == true ]] && default_str="y"
    local input
    input=$(prompt_user "$question (y/n)" "$default_str")
    [[ $input == "y" ]]
}

# Function to prompt user for selection input with a default value
prompt_selection() {
    local question=$1
    local default_value=$2
    local options=$3
    prompt_user "$question $options" "$default_value"
}

# Load existing configuration file
load_config() {
    if [[ -f $CONFIG_FILE ]]; then
        jq -r '.' "$CONFIG_FILE"
    else
        echo "{}"
    fi
}

# Save configuration to file
save_config() {
    local config=$1
    mkdir -p "$CONFIG_DIR"
    echo "$config" | jq '.' > "$CONFIG_FILE"
}

# Main function to handle configuration
main() {
    local skip_config=false
    [[ $1 == "--skip-config" ]] && skip_config=true

    local config
    config=$(load_config)

    if ! $skip_config; then
        echo "Please configure your settings:"

        local api_key
        api_key=$(echo "$config" | jq -r '.api_key // empty')
        api_key=$(prompt_user "Enter your API key" "$api_key")

        local domain
        domain=$(echo "$config" | jq -r '.domain // empty')
        domain=$(prompt_user "Enter the base domain" "$domain")
        [[ -z $domain ]] && domain=$DEFAULT_DOMAIN

        local image_type
        image_type=$(echo "$config" | jq -r '.image_type // empty')
        image_type=$(prompt_user "Enter image type (PNG, JPEG, GIF)" "$image_type")
        [[ -z $image_type ]] && image_type=$DEFAULT_IMAGE_TYPE

        local compression_level
        compression_level=$(echo "$config" | jq -r '.compression_level // empty')
        if [[ $image_type == "png" ]]; then
            compression_level=$(prompt_int "Enter PNG compression level (0-9)" "$compression_level")
            [[ $compression_level -lt 0 || $compression_level -gt 9 ]] && compression_level=$DEFAULT_COMPRESSION_LEVEL
        else
            compression_level=$DEFAULT_COMPRESSION_LEVEL
        fi

        local save_to_disk
        save_to_disk=$(echo "$config" | jq -r '.save_to_disk // empty')
        save_to_disk=$(prompt_bool "Save screenshot to disk" "$save_to_disk")

        local upload_to_api
        upload_to_api=$(echo "$config" | jq -r '.upload_to_api // empty')
        upload_to_api=$(prompt_bool "Upload screenshot to API" "$upload_to_api")

        local verbose
        verbose=$(echo "$config" | jq -r '.verbose // empty')
        verbose=$(prompt_bool "Enable verbose mode" "$verbose")

        local text_plugin_enabled
        text_plugin_enabled=$(echo "$config" | jq -r '.text_plugin_enabled // empty')
        text_plugin_enabled=$(prompt_bool "Enable text processing plugin" "$text_plugin_enabled")

        local screenshot_tool
        screenshot_tool=$(echo "$config" | jq -r '.screenshot_tool // empty')
        screenshot_tool=$(prompt_selection "Select screenshot tool (grim or flameshot)" "$screenshot_tool" "(grim or flameshot)")
        [[ -z $screenshot_tool ]] && screenshot_tool=$DEFAULT_SCREENSHOT_TOOL
    fi

    local new_config=$(jq -n --arg api_key "$api_key" --arg domain "$domain" --arg image_type "$image_type" --arg compression_level "$compression_level" --arg save_to_disk "$save_to_disk" --arg upload_to_api "$upload_to_api" --arg verbose "$verbose" --arg text_plugin_enabled "$text_plugin_enabled" --arg screenshot_tool "$screenshot_tool" '{api_key: $api_key, domain: $domain, image_type: $image_type, compression_level: $compression_level, save_to_disk: $save_to_disk, upload_to_api: $upload_to_api, verbose: $verbose, text_plugin_enabled: $text_plugin_enabled, screenshot_tool: $screenshot_tool}')

    save_config "$new_config"

    echo "Configuration saved successfully to: $CONFIG_FILE"
}

main "$@"
