# Image Viewer

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

A professional, feature-rich image viewer application built with Python, Tkinter, and ttkbootstrap. View images with EXIF metadata, navigate through folders seamlessly, and visualize photo locations on interactive maps.

## 🚀 Features

### Core Functionality
- **Multi-format support**: PNG, JPG, JPEG, GIF, BMP, and WebP
- **Folder navigation**: Seamlessly browse through all images in a directory
- **Keyboard shortcuts**: Intuitive navigation with arrow keys and F11 for fullscreen
- **Responsive design**: Modern dark theme with ttkbootstrap

### Metadata & Location
- **EXIF data extraction**: View capture date, GPS coordinates, and device information
- **Address geocoding**: Convert GPS coordinates to human-readable addresses
- **Interactive maps**: Visualize photo locations using Folium-powered maps
- **Device details**: Camera make, model, and technical specifications

### User Experience
- **Fullscreen mode**: Immersive viewing experience (F11)
- **Error handling**: Comprehensive logging and user-friendly error messages
- **Professional UI**: Clean, modern interface optimized for image viewing

## 📦 Installation

### Prerequisites
- Python 3.8.1 or higher
- System dependencies (Ubuntu/Debian/Xubuntu):
  ```bash
  sudo apt-get update
  sudo apt-get install python3-tk libwebp-dev
  ```

### Quick Start
1. **Clone the repository**
   ```bash
   git clone https://github.com/Onehand-Coding/image-viewer.git
   cd image-viewer
   ```

2. **Install dependencies**
   ```bash
   # Install all dependencies
   uv sync

   # Include development dependencies (optional)
   uv sync --extra dev
   ```

3. **Run the application**
   ```bash
   uv run src/custom_image_viewer/main.py
   # or
   uv run image-viewer
   ```

## 🎯 Usage

### Getting Started
1. **Open an image**: `File > Open Image` or use the file dialog
2. **Navigate**: Use arrow keys or Previous/Next buttons
3. **View metadata**: Access `Info` menu for EXIF data
4. **Map view**: Click "View on map" for GPS-enabled images
5. **Fullscreen**: Press `F11` for immersive viewing

### Keyboard Shortcuts
| Key | Action |
|-----|--------|
| `←` / `→` | Navigate between images |
| `F11` | Toggle fullscreen mode |
| `Ctrl+O` | Open image file |
| `Esc` | Exit fullscreen |

### Menu Options
- **File**: Open images, exit application
- **Info**: View EXIF data (date, location, device)
- **Help**: About dialog and version information

## 🏗️ Project Structure

```
custom-image-viewer/
├── src/
│   └── custom_image_viewer/
│       ├── __init__.py         # Package initialization
│       ├── config.py           # Configuration settings
│       ├── image_info.py       # EXIF metadata handling
│       ├── image_viewer.py     # Main GUI components
│       └── main.py             # Application entry point
├── data/                       # Generated files (maps, cache)
├── logs/                       # Application logs
├── tests/
│   └── test_image_info.py      # Unit tests
├── pyproject.toml              # Project configuration
├── requirements.txt            # Dependencies list
└── README.md                   # This file
```

## 🔧 Dependencies

### Core Libraries
- `ttkbootstrap>=1.10.1` - Modern UI components
- `Pillow>=10.0.0` - Image processing and format support
- `pyexiv2>=2.14.0` - EXIF metadata extraction
- `folium>=0.17.0` - Interactive map generation
- `geopy>=2.4.1` - Geocoding services

### Development Tools
- `pytest-mock` - Testing framework
- `ruff` - Code linting and formatting

## 🧪 Development

### Testing
```bash
# Run tests with coverage
uv run pytest --cov=src/custom_image_viewer tests/

# Run all tests
uv run pytest
```

### Code Quality
```bash
# Check code style
uv run ruff check

# Format code
uv run ruff format
```

### Logging Configuration
Modify logging settings in `src/custom_image_viewer/config.py`:
- `LOG_LEVEL`: Set to `DEBUG`, `INFO`, `WARNING`, or `ERROR`
- `LOG_FILE`: Change log file location (default: `logs/image_viewer.log`)

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Guidelines
- Follow PEP 8 style guidelines
- Add tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting

## 📋 Requirements

### System Requirements
- **OS**: Linux (Ubuntu/Debian tested), Windows, macOS
- **Python**: 3.8.1 or higher
- **Memory**: 512MB RAM minimum
- **Storage**: 50MB for application and dependencies

### Platform-Specific Notes
- **Linux**: Requires `python3-tk` and `libwebp-dev` packages
- **Windows**: No additional system dependencies
- **macOS**: May require Homebrew for some dependencies

## 🐛 Troubleshooting

### Common Issues
- **WebP not supported**: Install `libwebp-dev` system package
- **Tkinter import error**: Install `python3-tk` package
- **EXIF data not showing**: Ensure `pyexiv2` is properly installed
- **Map not opening**: Check internet connection and browser settings

### Getting Help
- 📝 [Report bugs](https://github.com/Onehand-Coding/image-viewer/issues)
- 💡 [Request features](https://github.com/Onehand-Coding/image-viewer/issues)
- 📖 [View documentation](https://github.com/Onehand-Coding/image-viewer/wiki)

## 📄 License

Copyright © 2025 Onehand Coding. This project is licensed under the [MIT License](LICENSE).

## 🌟 Acknowledgments

- Built with [ttkbootstrap](https://github.com/israel-dryer/ttkbootstrap) for modern UI
- Maps powered by [Folium](https://github.com/python-visualization/folium)
- EXIF handling via [pyexiv2](https://github.com/LeoHsiao1/pyexiv2)
- Geocoding services by [geopy](https://github.com/geopy/geopy)
