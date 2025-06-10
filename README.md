# Fontshare Bulk Font Downloader

A Python tool to download all fonts from [Fontshare.com](https://www.fontshare.com/) using their API endpoint. Since Fontshare doesn't provide a bulk download option, this tool automates the process of downloading their entire font library.

## Features

- 🔍 **Auto-discovery**: Automatically finds all available fonts on Fontshare
- 📥 **Bulk download**: Downloads all fonts using their API endpoint
- ⚡ **Concurrent downloads**: Configurable concurrent downloads with rate limiting
- 📊 **Progress tracking**: Real-time progress bars and detailed logging
- 🔄 **Resume capability**: Skips already downloaded fonts
- 📁 **Organized storage**: Saves fonts in organized directory structure

## Installation

1. **Clone or download this repository**

   ```bash
   cd /path/to/fonshare-download-all
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage

```bash
python fontshare_downloader.py
```

This will:

- Create a `downloads` folder in the current directory
- Discover all fonts from Fontshare
- Download each font as a ZIP file
- Save fonts in `downloads/fonts/` with organized subdirectories

### Advanced Usage

```bash
# Custom output directory
python fontshare_downloader.py --output-dir ./my-fonts

# Adjust rate limiting (delay between requests)
python fontshare_downloader.py --rate-limit 2.0

# Increase concurrent downloads
python fontshare_downloader.py --max-concurrent 5

# Enable verbose logging
python fontshare_downloader.py --verbose

# Combine options
python fontshare_downloader.py \
    --output-dir ./fontshare-collection \
    --rate-limit 0.5 \
    --max-concurrent 3 \
    --verbose
```

### Command Line Options

| Option                   | Description                      | Default       |
| ------------------------ | -------------------------------- | ------------- |
| `--output-dir`, `-o`     | Output directory for downloads   | `./downloads` |
| `--rate-limit`, `-r`     | Delay between requests (seconds) | `1.0`         |
| `--max-concurrent`, `-c` | Maximum concurrent downloads     | `3`           |
| `--verbose`, `-v`        | Enable verbose logging           | `False`       |

## Output Structure

After running the tool, your files will be organized as follows:

```
downloads/
├── fonts/                    # Downloaded font files
│   ├── satoshi/
│   │   └── satoshi.zip
│   ├── cabinet-grotesk/
│   │   └── cabinet-grotesk.zip
│   └── clash-display/
│       └── clash-display.zip
├── logs/                     # Log files
│   └── download.log
└── metadata/                 # Download metadata
    └── font-list.json
```

## How It Works

1. **Font Discovery**: The tool visits Fontshare and discovers all available fonts through multiple strategies:

   - Checking for API endpoints that list fonts
   - Parsing the website for embedded font data
   - Using a fallback list of known fonts

2. **Download Process**: For each discovered font, it:

   - Constructs the download URL: `https://api.fontshare.com/v2/fonts/download/{font-name}`
   - Downloads the font ZIP file
   - Saves it in an organized directory structure
   - Implements rate limiting to be respectful to the server

3. **Progress Tracking**: Shows real-time progress and logs all activities

## Example Output

```
🚀 Fontshare Bulk Font Downloader
========================================
🔍 Discovering fonts from Fontshare...
✅ Found 127 fonts via website parsing
📥 Starting download of 127 fonts...

Downloading fonts: 100%|████████████| 127/127 [05:23<00:00,  2.55s/font]

==================================================
🎉 Fontshare Bulk Download Complete!
==================================================
📁 Fonts saved to: ./downloads/fonts
📊 Success: 125 fonts
❌ Failed: 2 fonts
⏱️  Total time: 323.1 seconds
📋 Logs saved to: ./downloads/logs/download.log
```

## Rate Limiting & Ethics

This tool implements rate limiting to be respectful to Fontshare's servers:

- Default 1-second delay between downloads
- Configurable concurrent download limits
- Respectful user-agent and request patterns

Please use this tool responsibly and respect Fontshare's terms of service.

## Troubleshooting

### No fonts discovered

- Check your internet connection
- Fontshare might have changed their website structure
- The tool will fall back to a known list of popular fonts

### Download failures

- Some fonts might be temporarily unavailable
- Check the log file for detailed error information
- Failed downloads can be retried by running the tool again

### Permission errors

- Make sure you have write permissions in the output directory
- On Windows, you might need to run as administrator

## Font Usage

All fonts downloaded are subject to Fontshare's licensing terms. Please review their [license](https://www.fontshare.com/licenses) before using the fonts in your projects.

## Contributing

Feel free to contribute improvements:

- Better font discovery methods
- Additional output formats
- GUI interface
- Bug fixes and optimizations

## Disclaimer

This tool is for educational and personal use. Please respect Fontshare's terms of service and use their fonts according to their licensing terms. The fonts are provided by Fontshare under their own license agreements.
