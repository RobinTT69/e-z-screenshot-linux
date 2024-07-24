package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"os"
	"strconv"
)

type Config struct {
	APIKey           string `json:"api_key"`
	Domain           string `json:"domain"`
	FileType         string `json:"file_type"`
	CompressionLevel int    `json:"compression_level"`
}

func main() {
	configPath := os.ExpandEnv("$HOME/.config/e-zshot/config.json")

	config := loadConfig(configPath)

	fmt.Println("Current Configuration:")
	fmt.Printf("API Key: %s\n", config.APIKey)
	fmt.Printf("Domain: %s\n", config.Domain)
	fmt.Printf("File Type: %s\n", config.FileType)
	fmt.Printf("Compression Level: %d\n", config.CompressionLevel)

	fmt.Println("\nEnter new values (leave blank to keep current value):")

	var input string

	fmt.Print("API Key: ")
	fmt.Scanln(&input)
	if input != "" {
		config.APIKey = input
	}

	fmt.Print("Domain: ")
	fmt.Scanln(&input)
	if input != "" {
		config.Domain = input
	}

	fmt.Print("File Type: ")
	fmt.Scanln(&input)
	if input != "" {
		config.FileType = input
	}

	fmt.Print("Compression Level: ")
	fmt.Scanln(&input)
	if input != "" {
		compressionLevel, err := strconv.Atoi(input)
		if err == nil {
			config.CompressionLevel = compressionLevel
		} else {
			fmt.Println("Invalid compression level. Keeping current value.")
		}
	}

	saveConfig(configPath, config)
	fmt.Println("Configuration updated.")
}

func loadConfig(path string) Config {
	file, err := ioutil.ReadFile(path)
	if err != nil {
		fmt.Println("Error reading config file, using default values.")
		return Config{
			FileType:         "PNG",
			CompressionLevel: 6,
		}
	}

	var config Config
	if err := json.Unmarshal(file, &config); err != nil {
		fmt.Println("Error parsing config file, using default values.")
		return Config{
			FileType:         "PNG",
			CompressionLevel: 6,
		}
	}

	return config
}

func saveConfig(path string, config Config) {
	data, err := json.MarshalIndent(config, "", "  ")
	if err != nil {
		fmt.Println("Error saving config file.")
		return
	}

	if err := ioutil.WriteFile(path, data, 0644); err != nil {
		fmt.Println("Error writing config file.")
	}
}
