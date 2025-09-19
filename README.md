# Place Bot - Pixel Art Automation Tool for Wplace.live

A Python GUI application for automating pixel art creation on wplace.live canvases. The bot analyzes canvas regions, detects available colors, and automatically paints pixels to match your target image.

## Status: ✅ Working

## 🚨 Disclaimer

This tool is intended for **personal use and experimentation** on wplace.live. Use responsibly and respect the platform's rules and guidelines. Any use of this tool is at your own risk.

**Ban Status**: 0 reports ✅

## 🚀 Quick Start

**Requirements**: wplace.live, Blue Marble setup.

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

- 🎨 **Smart Color Detection** - Automatically detects available colors from palette
- 🖱️ **Visual Region Selection** - Drag-to-select canvas and palette areas
- ⚙️ **Customizable Settings** - Adjustable tolerance, delays, and pixel limits
- 🎯 **Precision Painting** - Finds and paints only pixels that need changes
- 📊 **Real-time Monitoring** - Progress tracking and debug visualization
- 💾 **Persistent Settings** - Saves your preferences and region selections

## 📖 Usage Guide

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

## ⚙️ How It Works

1. **🔍 Analysis**: Screenshots your selected regions and detects canvas patterns
2. **📋 Planning**: Compares current state with target to find pixels needing changes  
3. **🎨 Execution**: Systematically paints required pixels with appropriate colors
4. **📊 Monitoring**: Real-time feedback with respect for user-defined limits

## 💾 Configuration

Settings auto-save to `user_settings.json`:
- **Regions**: Canvas and palette coordinates
- **Preferences**: Tolerance, delays, pixel limits  
- **Colors**: Enabled status and premium ownership

## 🛡️ Safety Features

- **🎯 Pixel Limits**: Prevents runaway painting
- **⛔ Emergency Stop**: Manual halt button
- **🎛️ Tolerance Control**: Avoids unnecessary repainting
- **⏱️ Speed Control**: Configurable delays for stealth

## 🤝 Contributing

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

### 🏗️ Architecture Overview

```
wplace_bot/
├── app.py                 # 🎯 Main coordinator
├── main.py                # 🔍 Computer vision & analysis  
├── core/                  # 🧠 Business logic
│   ├── data_manager.py    # 💾 Data persistence
│   ├── analysis_worker.py # 🔬 Analysis threading
│   └── bot_worker.py      # 🤖 Bot threading
└── gui/                   # 🖥️ User interface
    ├── region_selector.py # 📐 Screen selection
    └── tabs/              # 📑 Tab components
```

### 📝 Development Guidelines

- **Clean Code**: Descriptive names, docstrings, single responsibility
- **Separation**: UI logic separate from business logic  
- **Error Handling**: User-friendly error messages
- **Testing**: Thoroughly test before submitting

### 🚀 Submitting Changes
1. **Test** thoroughly
2. **Document** changes  
3. **Commit** clearly: `git commit -m "Add: feature description"`
4. **Push**: `git push origin feature/amazing-feature`
5. **PR**: Create Pull Request with detailed description

## 🐛 Reporting Issues

- **GitHub Issues** with clear reproduction steps
- **Screenshots** for UI problems
- **System info** (OS, Python version)
- **Check existing** issues first

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## ☕ Supporting This Project

If you find this tool useful, consider supporting its development:

[![Ko-fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/ciguliaz)

**Other ways to support:**
- ⭐ **Star** this repository
- 🐛 **Report** bugs and issues  
- 💡 **Suggest** new features
- 📢 **Share** with others who might find it useful
- 🤝 **Contribute** code improvements

Every bit of support helps maintain and improve this project! 

---