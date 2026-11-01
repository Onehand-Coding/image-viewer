# Image Viewer Hardening Design

Date: 2026-11-01
Status: Draft for user review
Repo: https://github.com/Onehand-Coding/image-viewer

## Context

The repository is an inactive public Tkinter image viewer from July 2025. It has
a clean package layout and a small test file, but the application has several
real defects and almost no coverage.

Known defects:

- `image_info.py` parses GPS EXIF values with `eval`, which is unsafe and does
  not apply N/S/E/W reference values.
- `image_viewer.py` calls `tk.messagebox.showinfo` without importing the
  `messagebox` module. The About dialog raises `AttributeError`.
- `view_location_on_map` assumes GPS coordinates exist. Images without GPS raise
  `TypeError`.
- `display_image` does not guard against an empty image list. `Image.open(None)`
  raises an uncaught `TypeError`.
- `config.py` creates `data/` and `logs/` inside the project at import time. The
  installed package may live in a read-only site-packages directory.
- Geocoding uses Nominatim without a timeout or a clear failure path.
- The test suite has three tests, all for `ImageInfo`, and no tests for the
  viewer, config, map output, or entry point.
- The README references a missing `requirements.txt`, the wrong run command,
  and keyboard shortcuts that are not implemented.
- There is no CI and no pytest or Ruff configuration.

## Goals

1. Remove the unsafe GPS parsing and parse coordinates correctly.
2. Make missing GPS, malformed EXIF, and empty image lists fail gracefully.
3. Fix the About dialog and the documented keyboard shortcuts.
4. Move data and log directories to user-writable locations with lazy creation.
5. Add meaningful tests for the non-UI logic, mocked UI behavior, and entry point.
6. Add CI, pytest/Ruff configuration, and accurate documentation.

## Non-goals

- Replacing Tkinter or ttkbootstrap.
- Adding new image formats or editing features.
- Bundling map tiles or offline geocoding.
- Running a real GUI in CI. Tests mock Tkinter and use no display.
- Changing the visual design.

## Architecture

Target files:

```
src/custom_image_viewer/
  __init__.py
  config.py          # user data/log directories, logging, constants
  image_info.py      # EXIF, safe GPS/date parsing, geocoding, map output
  image_viewer.py    # Tkinter view and event wiring
  main.py            # entry point
tests/
  conftest.py
  test_config.py
  test_image_info.py
  test_image_viewer.py
  test_main.py
.github/workflows/ci.yml
README.md
CONTEXT.md
pyproject.toml
```

Responsibilities:

- `config.py`: path resolution and logging only. No directory creation at import
  time.
- `image_info.py`: pure parsing helpers plus I/O for EXIF, geocoding, and map
  files. It must not import Tkinter.
- `image_viewer.py`: user interface. It may import Tkinter but must not perform
  network or filesystem writes beyond image loading.
- `main.py`: builds the window and starts the loop.

## Data and log directories

Add environment-aware helpers:

```python
def get_data_dir() -> Path:
    override = os.getenv("IMAGE_VIEWER_DATA_DIR")
    if override:
        return Path(override).expanduser()
    return Path.home() / ".local" / "share" / "image-viewer"


def get_log_dir() -> Path:
    override = os.getenv("IMAGE_VIEWER_LOG_DIR")
    if override:
        return Path(override).expanduser()
    return Path.home() / ".local" / "state" / "image-viewer" / "logs"
```

- No directory is created at import time.
- `configure_logging` creates the log directory and file handler lazily.
- `view_location_on_map` creates the data directory lazily.
- The README documents both environment overrides.

## Safe EXIF parsing

Replace `eval` with explicit rational parsing:

```python
def _parse_gps_component(value: str) -> float:
    total = 0.0
    for index, token in enumerate(value.split()):
        if "/" in token:
            numerator, denominator = token.split("/", 1)
            part = float(numerator) / float(denominator)
        else:
            part = float(token)
        total += part / (60**index)
    return total


def _parse_coordinate(value: str, ref: str | None) -> float | None:
    try:
        result = _parse_gps_component(value)
    except (ValueError, ZeroDivisionError):
        return None
    if ref in ("S", "W"):
        result = -result
    return round(result, 6)
```

`coordinates` returns `(latitude, longitude)` or `None`:

- Read `Exif.GPSInfo.GPSLatitude`, `GPSLatitudeRef`, `GPSLongitude`, and
  `GPSLongitudeRef`.
- Return `None` if either value is missing or malformed.
- Apply `S`/`W` as negative values.
- Round to six decimal places.

The parser must accept `"14/1 35/1 0/1"`, `"14 35 0"`, and decimal tokens. It
must reject non-numeric tokens without raising.

## Date and time parsing

`_parse_datetime_info` returns a `datetime` or `None`:

- Milliseconds since epoch, for example `"1616347542050"`.
- Alpha month format, for example `"Dec 8, 2018 8:14:03 AM"`.
- EXIF format, for example `"2017:04:01 18:57:18"`.
- Malformed input returns `None` and logs a warning instead of raising.

`date` and `time` properties return formatted strings or `None`.

## EXIF read guard

- `ImageInfo` accepts `Path | None`.
- `_read_exif_metadata` returns `{}` when the path is `None`, missing, or
  unreadable.
- `metadata` caches the first successful read for the instance.
- The existing `device_make`, `device_model`, and hidden-value behavior stay.

## Geocoding and map output

`address`:

- Return `None` when coordinates are missing.
- Use `Nominatim(user_agent="image-viewer", timeout=5)`.
- Catch `GeocoderTimedOut`, `GeocoderUnavailable`, and general exceptions.
- Return `None` on failure.

`view_location_on_map(output_dir: Path | None = None) -> Path | None`:

- Return `None` when coordinates are missing.
- Build the Folium map and marker as before.
- Write to `output_dir` when provided, otherwise `get_data_dir()`.
- Use a per-image file name: `<image-stem>_location.html`, falling back to
  `location.html` when there is no image path.
- Create the output directory lazily.
- Call `webbrowser.open` and return the generated path.

## Viewer fixes

- Import `messagebox` from `tkinter` and use `messagebox.showinfo` in the About
  dialog.
- Add the missing `Ctrl+O` binding for Open Image.
- Add an `Escape` binding that exits fullscreen when active.
- Guard `display_image` when `image_path` is `None`.
- Make `load_image` robust when the chosen file is not in the scanned list.
- Keep `resize_image`, navigation, status bar, and info menu behavior.
- Keep the viewer free of direct geocoding and map writes.

## Tests

`tests/conftest.py`:

- Add `src` to `sys.path`.
- Set `IMAGE_VIEWER_DATA_DIR` and `IMAGE_VIEWER_LOG_DIR` to temporary paths for
  tests that need them.

`test_config.py`:

- Default data and log directories.
- Environment overrides.
- `configure_logging` creates the log file and adds handlers.

`test_image_info.py`:

- Metadata caching.
- Device make and model.
- Date parsing for all three formats.
- Malformed date returns `None`.
- GPS parsing with N/E and S/W refs.
- Decimal and rational token forms.
- Missing or malformed GPS returns `None`.
- `address` with a mocked geocoder, including the timeout.
- `address` returns `None` when geocoding fails.
- `view_location_on_map` writes an HTML file to a temporary directory and calls
  `webbrowser.open`.
- `view_location_on_map` returns `None` and does not open a browser without GPS.
- EXIF read failure returns `{}` without raising.

`test_image_viewer.py`:

- `is_image` accepts supported suffixes and rejects directories.
- `image_path` clamps the index and returns `None` for an empty list.
- `resize_image` preserves aspect ratio for landscape, portrait, and square.
- `load_image` populates the folder list with mocked file dialog and display.
- Previous and next navigation call `display_image` and close the info window.
- `update_status_bar` and `update_nav_button_state` with mock widgets.
- `toggle_fullscreen` flips the attribute and updates the menu label.
- `show_about_dialog` calls `messagebox.showinfo`.
- `add_info_menu` and `remove_info_menu` with a mock menu bar.

`test_main.py`:

- Patch `ttk.Window`, `ImageViewer`, and `configure_logging`.
- Assert the window, viewer, and `mainloop` are invoked.

## Tooling and CI

`pyproject.toml`:

- `requires-python = ">=3.10"`.
- Add `[tool.pytest.ini_options]` with `testpaths = ["tests"]`.
- Add `[tool.ruff]` with line length 88, target py310, and rules E, F, I, UP, B.
- Keep the existing dev dependencies.

`.github/workflows/ci.yml`:

1. Checkout.
2. Set up Python 3.12.
3. Set up uv.
4. `uv sync --extra dev`.
5. `uv run ruff check .`.
6. `uv run ruff format --check .`.
7. `uv run pytest`.
8. `uv build` and verify the wheel contains the package.

## Documentation

- README:
  - Correct Python version, install command, and run command.
  - Implemented shortcuts only: Left/Right, Ctrl+O, F11, Escape.
  - Data and log directory locations and environment overrides.
  - Map and geocoding behavior, including the no-GPS path.
  - Testing and CI commands.
  - Remove the missing `requirements.txt` reference.
- `CONTEXT.md`: architecture, data flow, commands, decisions, gotchas.
- No new screenshots are required.

## Acceptance criteria

1. No `eval` remains in `src`.
2. GPS coordinates parse safely, apply N/S/E/W, and return `None` on bad input.
3. Images without GPS do not crash the map action.
4. The About dialog works.
5. Data and log directories are configurable and created lazily.
6. Tests cover config, EXIF/date/GPS parsing, geocoding, map output, viewer
   helpers, and the entry point.
7. `ruff check`, `ruff format --check`, and `pytest` pass locally and in CI.
8. README and CONTEXT match the implementation.
9. The package builds and the wheel contains `custom_image_viewer`.

## Risks and mitigations

- Tkinter cannot open windows in CI. Tests mock widgets and never create a real
  root window.
- `pyexiv2` may be unavailable or platform-specific. Tests mock metadata; the
  runtime keeps a clear error path.
- Nominatim is a network service. Tests mock it; runtime uses a five-second
  timeout and returns `None` on failure.
- Folium map generation is file-only and does not need network access.
- Moving directories could surprise users. Document the new defaults and the
  environment overrides.
