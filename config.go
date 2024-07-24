package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"os"
	"strings"
)

// Config structure to hold user settings
type Config struct {
	APIKey            string `json:"api_key"`
	Domain            string `json:"domain"`
	ImageType         string `json:"image_type"`
	CompressionLevel  int    `json:"compression_level"`
	SaveToDisk        bool   `json:"save_to_disk"`
	UploadToAPI       bool   `json:"upload_to_api"`
	Verbose           bool   `json:"verbose"`
	TextPluginEnabled bool   `json:"text_plugin_enabled"`
}

// Default configuration values
const (
	defaultDomain           = "https://i.e-z.host"
	defaultImageType        = "PNG"
	defaultCompressionLevel = 6
)

// Read user input with default value and prompt
func promptUser(question string, defaultValue string) string {
	reader := bufio.NewReader(os.Stdin)
	fmt.Printf("%s [%s]: ", question, defaultValue)
	input, _ := reader.ReadString('\n')
	input = strings.TrimSpace(input)
	if input == "" {
		return defaultValue
	}
	return input
}

// Read integer user input with default value
func promptInt(question string, defaultValue int) int {
	defaultStr := fmt.Sprintf("%d", defaultValue)
	input := promptUser(question, defaultStr)
	var value int
	fmt.Sscanf(input, "%d", &value)
	if value == 0 {
		return defaultValue
	}
	return value
}

// Read boolean user input with default value
func promptBool(question string, defaultValue bool) bool {
	defaultStr := "n"
	if defaultValue {
		defaultStr = "y"
	}
	input := promptUser(question+" (y/n)", defaultStr)
	return strings.ToLower(input) == "y"
}

// Load existing configuration file
func loadConfig() (*Config, error) {
	configFile := os.Getenv("HOME") + "/.config/e-zshot/config.json"
	file, err := os.Open(configFile)
	if err != nil {
		if os.IsNotExist(err) {
			return nil, nil
		}
		return nil, err
	}
	defer file.Close()

	var config Config
	decoder := json.NewDecoder(file)
	err = decoder.Decode(&config)
	if err != nil {
		return nil, err
	}
	return &config, nil
}

// Main function to handle configuration
func main() {
	// Check for skip config argument
	skipConfig := len(os.Args) > 1 && os.Args[1] == "--skip-config"

	// Load previous configuration if it exists
	config, err := loadConfig()
	if err != nil {
		fmt.Println("Error loading configuration:", err)
		os.Exit(1)
	}

	// Prompt user for configuration with defaults from previous settings
	if !skipConfig {
		fmt.Println("Please configure your settings:")

		if config == nil {
			config = &Config{}
		}

		config.APIKey = promptUser("Enter your API key", config.APIKey)
		config.Domain = promptUser("Enter the base domain", config.Domain)
		if config.Domain == "" {
			config.Domain = defaultDomain
		}
		config.ImageType = promptUser("Enter image type (PNG, JPEG, GIF)", config.ImageType)
		if config.ImageType == "" {
			config.ImageType = defaultImageType
		}
		config.CompressionLevel = promptInt("Enter PNG compression level (0-9)", config.CompressionLevel)
		if config.CompressionLevel < 0 || config.CompressionLevel > 9 {
			config.CompressionLevel = defaultCompressionLevel
		}
		config.SaveToDisk = promptBool("Save screenshot to disk", config.SaveToDisk)
		config.UploadToAPI = promptBool("Upload screenshot to API", config.UploadToAPI)
		config.Verbose = promptBool("Enable verbose mode", config.Verbose)
		config.TextPluginEnabled = promptBool("Enable text processing plugin", config.TextPluginEnabled)
	}

	// Create config directory if it doesn't exist
	configDir := os.Getenv("HOME") + "/.config/e-zshot"
	if _, err := os.Stat(configDir); os.IsNotExist(err) {
		err = os.MkdirAll(configDir, 0755)
		if err != nil {
			fmt.Println("Error creating configuration directory:", err)
			os.Exit(1)
		}
	}

	// Save configuration to file
	configFile := configDir + "/config.json"
	file, err := os.Create(configFile)
	if err != nil {
		fmt.Println("Error creating configuration file:", err)
		os.Exit(1)
	}
	defer file.Close()

	encoder := json.NewEncoder(file)
	encoder.SetIndent("", "  ")
	err = encoder.Encode(config)
	if err != nil {
		fmt.Println("Error writing configuration file:", err)
		os.Exit(1)
	}

	fmt.Println("Configuration saved successfully to:", configFile)
}
