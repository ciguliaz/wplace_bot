# Place Bot - Pixel Art Automation Tool for Wplace.live

A Python GUI application for automating pixel art creation on wplace.live canvases. The bot analyzes canvas regions, detects available colors, and automatically paints pixels to match your target image.

## Status: Working

## Disclaimer

This tool is intended for **personal use and experimentation** on wplace.live. Use responsibly and respect the platform's rules and guidelines. Any use of this tool is at your own risk.

**Ban Status**: 0 reports

## Quick Start

**Requirements**: wplace.live, Blue Marble setup, and template image went through blue marble color converting.

### Option 1: From Release (Recommended)

1. **Download** the latest release from [Releases](https://github.com/ciguliaz/wplace_bot/releases)
2. **Extract** the files (should include `app.exe` and `colors.json`)
3. **Run** `app.exe`
4. **Allow** through Windows Defender/antivirus if prompted
5. **Follow** the in-app instructions

### Option 2: From Source

**Requirements**: Python 3.8+

1. **Clone** the repository:
   ```bash
   git clone https://github.com/ciguliaz/wplace_bot.git
   cd wplace_bot
   ```

2. **Install** dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run** the application:
   ```bash
   python app.py
   ```

## Features

- **Smart Color Detection** - Automatically detects available colors from palette
- **Visual Region Selection** - Drag-to-select canvas and palette areas
- **Customizable Settings** - Adjustable tolerance, delays, and pixel limits
- **Precision Painting** - Finds and paints only pixels that need changes
- **Real-time Monitoring** - Progress tracking and debug visualization
- **Persistent Settings** - Saves your preferences and region selections
- **Centralized Logging** - File and console logging with GUI feedback
- **Modular Architecture** - Clean separation of GUI, core logic, and workers

## Usage Guide

### 1. Setup Tab
- Click **"Select Canvas"** → Drag to select the drawing area
- Click **"Select Palette"** → Drag to select the color palette  
- Adjust **color tolerance** and **click delay** settings
- Click **"Analyze Canvas & Palette"**

### 2. Color Control Tab
- **Enable/disable** colors you want to use
- Mark premium colors as **"bought"** if you own them
- Use quick buttons: **"Enable All"**, **"Free Colors"**, etc.

### 3. Bot Control Tab
- Set **pixel limit** (stops after painting X pixels)
- Click **"Start Painting"** to begin automation
- Monitor progress in real-time
- Click **"Stop"** to halt immediately

### 4. Preview & Debug Tab
- View analysis results and debug images
- Check detected pixel sizes and color mappings

## How It Works

1. **Analysis**: Screenshots your selected regions and detects canvas patterns
2. **Planning**: Compares current state with target to find pixels needing changes  
3. **Execution**: Systematically paints required pixels with appropriate colors
4. **Monitoring**: Real-time feedback with respect for user-defined limits

## Configuration

Settings auto-save to `user_settings.json`:
- **Regions**: Canvas and palette coordinates
- **Preferences**: Tolerance, delays, pixel limits  
- **Colors**: Enabled status and premium ownership

## Safety Features

- **Pixel Limits**: Prevents runaway painting
- **Emergency Stop**: Manual halt button
- **Tolerance Control**: Avoids unnecessary repainting
- **Speed Control**: Configurable delays for stealth

## Contributing

### Getting Started
1. **Fork** this repository
2. **Clone** your fork:
   ```bash
   git clone https://github.com/yourusername/wplace_bot.git
   ```
3. **Create** feature branch:
   ```bash
   git checkout -b feature/amazing-feature
   ```
4. **Install** dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Architecture Overview

```
wplace_bot/
├── app.py                   # Main GUI application entry point
├── main.py                  # Terminal interface for command-line usage
├── core/                    # Core business logic and workers
│   ├── __init__.py          # Core module exports
│   ├── data_manager.py      # Settings and data persistence
│   ├── analysis_worker.py   # Canvas analysis in separate thread
│   ├── bot_worker.py        # Painting automation in separate thread
│   ├── logger.py            # Centralized logging system
│   ├── screen_capture.py    # Screenshot functionality
│   ├── image_analysis.py    # Computer vision and pixel detection
│   ├── color_detection.py   # Palette color detection
│   ├── automation.py        # Mouse click automation
│   └── pixel_mapping.py     # Pixel mapping and painting logic
└── gui/                     # User interface components
    ├── __init__.py          # GUI module exports
    ├── region_selector.py   # Interactive screen region selection
    └── tabs/                # Individual tab implementations
        ├── __init__.py      # Tab module exports
        ├── setup_tab.py     # Canvas/palette setup and analysis
        ├── colors_tab.py    # Color enable/disable controls
        ├── control_tab.py   # Bot control and logging
        └── preview_tab.py   # Analysis results and debug info
```

### Development Guidelines

- **Clean Code**: Descriptive names, docstrings, single responsibility
- **Separation**: UI logic separate from business logic  
- **Error Handling**: User-friendly error messages
- **Testing**: Thoroughly test before submitting

### Submitting Changes
1. **Test** thoroughly
2. **Document** changes  
3. **Commit** clearly: `git commit -m "Add: feature description"`
4. **Push**: `git push origin feature/amazing-feature`
5. **PR**: Create Pull Request with detailed description

## Reporting Issues

- **GitHub Issues** with clear reproduction steps
- **Screenshots** for UI problems
- **System info** (OS, Python version)
- **Check existing** issues first

## Technical Details

### Core Components

- **DataManager**: Handles settings persistence, color palette loading, and analysis data storage
- **AnalysisWorker**: Performs canvas analysis in background thread to avoid GUI blocking
- **BotWorker**: Executes painting automation in background thread with progress reporting
- **Logger**: Centralized logging with file output, console output, and GUI callback support

### Image Processing

- **Screen Capture**: Uses pyautogui for cross-platform screenshot functionality
- **Pixel Detection**: OpenCV-based computer vision for detecting canvas grid patterns
- **Color Matching**: Tolerance-based color comparison for robust palette detection
- **Pixel Mapping**: Builds comprehensive map of canvas pixels and their current colors

### GUI Architecture

- **Modular Tabs**: Each tab is a separate class for maintainability
- **Message Queue**: Thread-safe communication between workers and GUI
- **Event-Driven**: Responsive UI with proper cleanup and resource management

### Logging System

- **Multiple Outputs**: Console, file, and GUI logging simultaneously
- **Log Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL with appropriate filtering
- **Structured Events**: Specific logging methods for different application events
- **File Rotation**: Daily log files with timestamps for debugging

## License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## Supporting This Project

If you find this tool useful, consider supporting its development:

[![Ko-fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/ciguliaz)

**Other ways to support:**
- **Star** this repository
- **Report** bugs and issues  
- **Suggest** new features
- **Share** with others who might find it useful
- **Contribute** code improvements

Every bit of support helps maintain and improve this project! 

---