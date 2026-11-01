# Project Context

## Purpose

A local Tkinter image viewer with EXIF metadata, GPS geocoding, and Folium map
output. It targets desktop use and is not a hosted service.

## Architecture

- `config.py` owns path resolution, logging, and constants. It does not create
  directories at import time.
- `image_info.py` owns EXIF reading, date and GPS parsing, geocoding, and map
  file output. It does not import Tkinter.
- `image_viewer.py` owns the Tkinter view and event wiring.
- `main.py` builds the window and starts the main loop.

## Data Flow

Image path -> EXIF metadata -> date/device/GPS properties -> geocoding or map
output. The viewer reads these properties when the Info menu or map button is
used.

## Commands

```bash
uv sync --extra dev
uv run image-viewer
uv run ruff check .
uv run ruff format --check .
uv run pytest
```

## Decisions

- Keep Tkinter and ttkbootstrap; no framework rewrite.
- Parse GPS rationals explicitly instead of using `eval`.
- Apply N/S/E/W reference values.
- Keep geocoding optional and time-bounded.
- Write runtime files to user data and log directories.
- Mock Tkinter and network calls in tests.

## Gotchas

- Do not create `data/` or `logs/` in the project at import time.
- `ImageInfo` accepts a missing path and returns empty metadata.
- `coordinates` returns `None` for missing or malformed GPS data.
- `view_location_on_map` returns `None` when there are no coordinates.
- The About dialog must use `tkinter.messagebox`, not `tk.messagebox`.
- Folium needs a string path when saving.
- `ImageInfo.metadata` caches the first read; reset `_metadata` if a test needs
  to inject a different mapping after access.

## Known Limitations

- Geocoding requires network access and may be rate-limited.
- Map tiles are loaded by the browser, not bundled.
- Tests mock the GUI; there is no automated screenshot or visual regression test.
