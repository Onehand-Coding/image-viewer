# Image Viewer

[![CI](https://github.com/Onehand-Coding/image-viewer/actions/workflows/ci.yml/badge.svg)](https://github.com/Onehand-Coding/image-viewer/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

A desktop image viewer built with Tkinter and ttkbootstrap. It supports folder
navigation, EXIF metadata, GPS coordinates, address lookup, and Folium maps.

## Features

- Browse PNG, JPG, JPEG, GIF, BMP, and WebP images.
- Navigate with the arrow keys or Previous/Next buttons.
- View capture date, camera make/model, and GPS coordinates.
- Geocode GPS coordinates to an address.
- Open a Folium map for images with GPS data.
- Toggle fullscreen with F11 or Escape.
- Log errors without crashing the viewer.

## Install

Requirements: Python 3.10+ and [uv](https://github.com/astral-sh/uv).

System packages for Linux:

```bash
sudo apt-get update
sudo apt-get install python3-tk libwebp-dev
```

```bash
git clone https://github.com/Onehand-Coding/image-viewer.git
cd image-viewer
uv sync --extra dev
uv run image-viewer
```

## Usage

| Input | Action |
| --- | --- |
| Left arrow | Previous image |
| Right arrow | Next image |
| Ctrl+O | Open an image |
| F11 | Toggle fullscreen |
| Escape | Exit fullscreen |

Use **File > Open Image** to choose a file. The viewer scans the containing
folder and enables Previous/Next as needed. Use the **Info** menu to view the
date, location, or device details.

## Data and Logs

Runtime files live outside the project:

- Data: `~/.local/share/image-viewer`
- Logs: `~/.local/state/image-viewer/logs`

Override them with:

```bash
IMAGE_VIEWER_DATA_DIR=/tmp/image-viewer-data
IMAGE_VIEWER_LOG_DIR=/tmp/image-viewer-logs
```

Map files are written to the data directory as `<image-stem>_location.html`.

## Geocoding and Maps

Address lookup uses OpenStreetMap Nominatim through geopy with a five-second
timeout. It returns no address when offline or rate-limited. Map generation is
local and works without network access once coordinates are available. Images
without GPS data simply skip the map action.

## Development

```bash
uv sync --extra dev
uv run ruff check .
uv run ruff format --check .
uv run pytest
```

CI runs the same commands plus a wheel build. Tests mock Tkinter and network
calls, so no display or network is required.

## Project Structure

```text
src/custom_image_viewer/
  config.py          # paths, logging, constants
  image_info.py      # EXIF, dates, GPS, geocoding, map output
  image_viewer.py    # Tkinter view
  main.py            # entry point
tests/
  test_config.py
  test_image_info.py
  test_image_viewer.py
  test_main.py
```

## Troubleshooting

- **Tkinter import error:** install `python3-tk`.
- **WebP not supported:** install `libwebp-dev`.
- **No address shown:** geocoding needs network access and may be rate-limited.
- **No map action:** the image has no GPS coordinates in its EXIF data.

## License

MIT. See `LICENSE`.
