# Image Viewer Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Harden image-viewer by removing unsafe GPS parsing, fixing map/About/empty-image crashes, moving data and logs to user directories, adding meaningful tests, and adding CI and accurate docs.

**Architecture:** Keep the Tkinter view thin. Put EXIF, date, GPS, geocoding, and map output in `image_info.py` with pure helpers. Make `config.py` path and logging only, with lazy directory creation. Tests mock Tkinter and network calls.

**Tech Stack:** Python 3.10+, Tkinter, ttkbootstrap, Pillow, pyexiv2, folium, geopy, pytest, pytest-mock, ruff, uv, GitHub Actions.

**Git policy:** Do not run `git commit`, `git push`, or `git add` unless the user explicitly asks.

---

## File Map

Create or replace:

- `src/custom_image_viewer/config.py`
- `src/custom_image_viewer/image_info.py`
- `src/custom_image_viewer/image_viewer.py`
- `src/custom_image_viewer/main.py`
- `pyproject.toml`
- `.github/workflows/ci.yml`
- `tests/conftest.py`
- `tests/test_config.py`
- `tests/test_image_info.py`
- `tests/test_image_viewer.py`
- `tests/test_main.py`
- `README.md`
- `CONTEXT.md`

Do not touch:

- `LICENSE`
- `src/custom_image_viewer/__init__.py` unless a version bump is needed.

---

## Task 1: Config, Data Directories, and Test Bootstrap

**Files:**
- Replace: `src/custom_image_viewer/config.py`
- Modify: `pyproject.toml`
- Create: `.github/workflows/ci.yml`
- Create: `tests/conftest.py`
- Create: `tests/test_config.py`

- [ ] **Step 1: Write the failing config tests**

Create `tests/conftest.py`:

```python
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
```

Create `tests/test_config.py`:

```python
import logging
from pathlib import Path

from custom_image_viewer import config


def test_data_dir_default(monkeypatch):
    monkeypatch.delenv("IMAGE_VIEWER_DATA_DIR", raising=False)
    assert config.get_data_dir() == (
        Path.home() / ".local" / "share" / "image-viewer"
    )


def test_data_dir_override(monkeypatch, tmp_path):
    monkeypatch.setenv("IMAGE_VIEWER_DATA_DIR", str(tmp_path))
    assert config.get_data_dir() == tmp_path


def test_log_dir_default(monkeypatch):
    monkeypatch.delenv("IMAGE_VIEWER_LOG_DIR", raising=False)
    assert config.get_log_dir() == (
        Path.home() / ".local" / "state" / "image-viewer" / "logs"
    )


def test_log_dir_override(monkeypatch, tmp_path):
    monkeypatch.setenv("IMAGE_VIEWER_LOG_DIR", str(tmp_path))
    assert config.get_log_dir() == tmp_path


def test_configure_logging_creates_file(tmp_path):
    log_file = tmp_path / "logs" / "viewer.log"
    config.configure_logging(log_file=log_file)
    logging.getLogger("image-viewer-test").warning("hello")
    for handler in logging.getLogger().handlers:
        handler.flush()
    assert log_file.exists()
    assert "hello" in log_file.read_text()
```

- [ ] **Step 2: Run the tests and verify they fail**

Run:

```bash
uv sync --extra dev
uv run pytest tests/test_config.py -q
```

Expected: FAIL because `get_data_dir`, `get_log_dir`, and the new `configure_logging` signature do not exist.

- [ ] **Step 3: Replace `config.py`**

```python
from __future__ import annotations

import logging
import os
from pathlib import Path

APP_NAME = "Image Viewer"
APP_VERSION = "1.1"
MASTER_SIZE = "500x550"
INFO_WINDOW_SIZE = "300x150"
INFO_WINDOW_ALT_SIZE = "200x100"
SUPPORTED_IMAGE_FORMATS = (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp")
AVAILABLE_THEMES = ["darkly", "flatly", "litera"]
MAP_ZOOM_START = 15
MAP_POPUP_TEXT = "Image Location"
LOG_LEVEL = logging.INFO
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"


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


def configure_logging(
    log_level: int = LOG_LEVEL,
    log_file: Path | None = None,
) -> None:
    if log_file is None:
        log_file = get_log_dir() / "image_viewer.log"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    handlers: list[logging.Handler] = [
        logging.StreamHandler(),
        logging.FileHandler(log_file, mode="w"),
    ]
    logging.basicConfig(
        level=log_level,
        handlers=handlers,
        format=LOG_FORMAT,
        force=True,
    )
```

- [ ] **Step 4: Update `pyproject.toml`**

Set `requires-python = ">=3.10"` and append:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-ra"

[tool.ruff]
line-length = 88
target-version = "py310"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B"]
ignore = ["E501"]
```

- [ ] **Step 5: Create `.github/workflows/ci.yml`**

```yaml
name: CI

on:
  push:
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Set up uv
        uses: astral-sh/setup-uv@v6
        with:
          enable-cache: true

      - name: Install dependencies
        run: uv sync --extra dev

      - name: Lint
        run: uv run ruff check .

      - name: Format check
        run: uv run ruff format --check .

      - name: Test
        run: uv run pytest

      - name: Build wheel
        run: uv build

      - name: Check wheel contents
        run: python -m zipfile -l dist/*.whl | grep custom_image_viewer/config.py
```

- [ ] **Step 6: Run the config tests**

Run:

```bash
uv run pytest tests/test_config.py -q
```

Expected: 5 passed.

---

## Task 2: Safe EXIF, Date, and GPS Parsing

**Files:**
- Replace: `src/custom_image_viewer/image_info.py`
- Replace: `tests/test_image_info.py`

- [ ] **Step 1: Write the failing parsing tests**

Create `tests/test_image_info.py`:

```python
import datetime
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from custom_image_viewer import image_info
from custom_image_viewer.image_info import (
    ImageInfo,
    _parse_coordinate,
    _parse_gps_component,
)


def make_info(metadata):
    info = ImageInfo(Path("test.jpg"))
    info._metadata = metadata
    return info


def test_metadata_is_cached():
    info = ImageInfo(Path("test.jpg"))
    calls = []
    info._read_exif_metadata = lambda: calls.append(1) or {"Exif.Image.Model": "M"}
    assert info.metadata == {"Exif.Image.Model": "M"}
    assert info.metadata == {"Exif.Image.Model": "M"}
    assert len(calls) == 1


def test_device_properties():
    info = make_info(
        {"Exif.Image.Make": "TestMake", "Exif.Image.Model": "TestModel"}
    )
    assert info.device_make == "TestMake"
    assert info.device_model == "TestModel"


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("2021:03:21 12:34:56", datetime.datetime(2021, 3, 21, 12, 34, 56)),
        ("Dec 8, 2018 8:14:03 AM", datetime.datetime(2018, 12, 8, 8, 14, 3)),
    ],
)
def test_parse_datetime_formats(raw, expected):
    assert make_info({})._parse_datetime_info(raw) == expected


def test_parse_datetime_epoch():
    parsed = make_info({})._parse_datetime_info("1616347542050")
    assert parsed is not None
    assert parsed.year == 2021


def test_parse_datetime_bad_returns_none():
    assert make_info({})._parse_datetime_info("not a date") is None


def test_date_and_time():
    info = make_info({"Exif.Image.DateTime": "2021:03:21 12:34:56"})
    assert info.date == "March 21, 2021"
    assert info.time == "12:34 PM"


def test_gps_component_parsing():
    assert _parse_gps_component("14/1 35/1 0/1") == pytest.approx(
        14.583333, abs=1e-6
    )
    assert _parse_gps_component("14 35 0") == pytest.approx(14.583333, abs=1e-6)


def test_coordinate_refs():
    assert _parse_coordinate("14/1 35/1 0/1", "N") == 14.583333
    assert _parse_coordinate("14/1 35/1 0/1", "S") == -14.583333
    assert _parse_coordinate("bad", "N") is None


def test_coordinates_north_east():
    info = make_info(
        {
            "Exif.GPSInfo.GPSLatitude": "14/1 35/1 0/1",
            "Exif.GPSInfo.GPSLatitudeRef": "N",
            "Exif.GPSInfo.GPSLongitude": "120/1 58/1 0/1",
            "Exif.GPSInfo.GPSLongitudeRef": "E",
        }
    )
    assert info.coordinates == (14.583333, 120.966667)


def test_coordinates_south_west():
    info = make_info(
        {
            "Exif.GPSInfo.GPSLatitude": "14/1 35/1 0/1",
            "Exif.GPSInfo.GPSLatitudeRef": "S",
            "Exif.GPSInfo.GPSLongitude": "120/1 58/1 0/1",
            "Exif.GPSInfo.GPSLongitudeRef": "W",
        }
    )
    assert info.coordinates == (-14.583333, -120.966667)


def test_coordinates_missing_or_bad():
    assert make_info({}).coordinates is None
    assert (
        make_info(
            {
                "Exif.GPSInfo.GPSLatitude": "bad",
                "Exif.GPSInfo.GPSLongitude": "bad",
            }
        ).coordinates
        is None
    )


def test_address_uses_geocoder(monkeypatch):
    info = make_info(
        {
            "Exif.GPSInfo.GPSLatitude": "14/1 35/1 0/1",
            "Exif.GPSInfo.GPSLatitudeRef": "N",
            "Exif.GPSInfo.GPSLongitude": "120/1 58/1 0/1",
            "Exif.GPSInfo.GPSLongitudeRef": "E",
        }
    )
    geocoder = MagicMock()
    geocoder.reverse.return_value.address = "Somewhere"
    monkeypatch.setattr(image_info, "Nominatim", lambda **kwargs: geocoder)

    assert info.address == "Somewhere"
    geocoder.reverse.assert_called_once_with(
        (14.583333, 120.966667), language="en"
    )


def test_address_failure_returns_none(monkeypatch):
    info = make_info(
        {
            "Exif.GPSInfo.GPSLatitude": "14/1 35/1 0/1",
            "Exif.GPSInfo.GPSLongitude": "120/1 58/1 0/1",
        }
    )
    geocoder = MagicMock()
    geocoder.reverse.side_effect = image_info.GeocoderUnavailable("down")
    monkeypatch.setattr(image_info, "Nominatim", lambda **kwargs: geocoder)

    assert info.address is None


def test_view_location_on_map_writes_file(tmp_path, monkeypatch):
    info = make_info(
        {
            "Exif.GPSInfo.GPSLatitude": "14/1 35/1 0/1",
            "Exif.GPSInfo.GPSLatitudeRef": "N",
            "Exif.GPSInfo.GPSLongitude": "120/1 58/1 0/1",
            "Exif.GPSInfo.GPSLongitudeRef": "E",
        }
    )
    opened = []
    monkeypatch.setattr(
        image_info.webbrowser, "open", lambda url: opened.append(url)
    )

    map_file = info.view_location_on_map(tmp_path)

    assert map_file is not None
    assert map_file.exists()
    assert map_file.stat().st_size > 0
    assert opened == [str(map_file)]


def test_view_location_without_gps_returns_none(tmp_path, monkeypatch):
    info = make_info({})
    opened = []
    monkeypatch.setattr(
        image_info.webbrowser, "open", lambda url: opened.append(url)
    )

    assert info.view_location_on_map(tmp_path) is None
    assert opened == []


def test_read_exif_missing_file_returns_empty():
    assert ImageInfo(Path("missing.jpg")).metadata == {}
```

- [ ] **Step 2: Run the tests and verify they fail**

Run:

```bash
uv run pytest tests/test_image_info.py -q
```

Expected: FAIL because `_parse_gps_component`, `_parse_coordinate`, and the new behavior do not exist.

- [ ] **Step 3: Replace `image_info.py`**

```python
from __future__ import annotations

import datetime
import logging
import webbrowser
from pathlib import Path

import folium
import pyexiv2
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
from geopy.geocoders import Nominatim

from .config import MAP_POPUP_TEXT, MAP_ZOOM_START, get_data_dir

logger = logging.getLogger(__name__)


def _parse_gps_component(value: str) -> float:
    total = 0.0
    for index, token in enumerate(str(value).split()):
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


class ImageInfo:
    def __init__(self, image_path: Path | None):
        self.image_path = Path(image_path) if image_path is not None else None
        self._metadata: dict | None = None

    def _read_exif_metadata(self) -> dict:
        if self.image_path is None or not self.image_path.exists():
            return {}
        try:
            with open(self.image_path, "rb") as handle:
                with pyexiv2.ImageData(handle.read()) as image_info:
                    return image_info.read_exif()
        except Exception as exc:
            logger.error(
                "Error reading EXIF metadata for %s: %s",
                self.image_path,
                exc,
            )
            return {}

    @property
    def metadata(self) -> dict:
        if self._metadata is None:
            self._metadata = self._read_exif_metadata()
        return self._metadata

    @property
    def device_model(self):
        return self.metadata.get("Exif.Image.Model")

    @property
    def device_make(self):
        return self.metadata.get("Exif.Image.Make")

    def _parse_datetime_info(
        self, datetime_info: str
    ) -> datetime.datetime | None:
        try:
            if all(char.isdigit() for char in datetime_info):
                return datetime.datetime.fromtimestamp(
                    int(datetime_info) / 1000
                )
            if any(char.isalpha() for char in datetime_info):
                return datetime.datetime.strptime(
                    datetime_info, "%b %d, %Y %H:%M:%S %p"
                )
            return datetime.datetime.strptime(
                datetime_info, "%Y:%m:%d %H:%M:%S"
            )
        except (ValueError, OverflowError, OSError) as exc:
            logger.warning("Could not parse date %r: %s", datetime_info, exc)
            return None

    def get_datetime_info(self) -> str | None:
        for key in ("Exif.Image.DateTime", "Exif.Photo.DateTimeOriginal"):
            value = self.metadata.get(key)
            if value:
                return value
        if self.metadata:
            logger.error("No DateTime info extracted from %s.", self.image_path)
        return None

    @property
    def date(self):
        datetime_info = self.get_datetime_info()
        if not datetime_info:
            return None
        parsed = self._parse_datetime_info(datetime_info)
        return parsed.strftime("%B %d, %Y") if parsed else None

    @property
    def time(self):
        datetime_info = self.get_datetime_info()
        if not datetime_info:
            return None
        parsed = self._parse_datetime_info(datetime_info)
        return parsed.strftime("%I:%M %p") if parsed else None

    @property
    def coordinates(self) -> tuple[float, float] | None:
        latitude_info = self.metadata.get("Exif.GPSInfo.GPSLatitude")
        longitude_info = self.metadata.get("Exif.GPSInfo.GPSLongitude")
        if not latitude_info or not longitude_info:
            return None
        latitude = _parse_coordinate(
            latitude_info,
            self.metadata.get("Exif.GPSInfo.GPSLatitudeRef"),
        )
        longitude = _parse_coordinate(
            longitude_info,
            self.metadata.get("Exif.GPSInfo.GPSLongitudeRef"),
        )
        if latitude is None or longitude is None:
            return None
        return latitude, longitude

    @property
    def address(self):
        coordinates = self.coordinates
        if coordinates is None:
            return None
        latitude, longitude = coordinates
        geolocator = Nominatim(user_agent="image-viewer", timeout=5)
        try:
            location = geolocator.reverse(
                (latitude, longitude), language="en"
            )
        except (GeocoderTimedOut, GeocoderUnavailable) as exc:
            logger.error(
                "Geocoding unavailable for %s: %s", self.image_path, exc
            )
            return None
        except Exception as exc:
            logger.error(
                "Error during geocoding for %s: %s", self.image_path, exc
            )
            return None
        return location.address if location else None

    def view_location_on_map(
        self, output_dir: Path | None = None
    ) -> Path | None:
        coordinates = self.coordinates
        if coordinates is None:
            return None
        latitude, longitude = coordinates
        map_location = folium.Map(
            location=[latitude, longitude], zoom_start=MAP_ZOOM_START
        )
        folium.Marker(
            [latitude, longitude], popup=MAP_POPUP_TEXT
        ).add_to(map_location)
        target_dir = output_dir or get_data_dir()
        target_dir.mkdir(parents=True, exist_ok=True)
        stem = self.image_path.stem if self.image_path else "location"
        map_file = target_dir / f"{stem}_location.html"
        map_location.save(str(map_file))
        webbrowser.open(str(map_file))
        return map_file
```

- [ ] **Step 4: Run the parsing tests**

Run:

```bash
uv run pytest tests/test_image_info.py -q
```

Expected: all parsing and map tests pass.

---

## Task 3: Geocoding and Map Edge Cases

**Files:**
- Modify: `tests/test_image_info.py` only if a gap remains after Task 2.

Task 2 already covers geocoder success, geocoder failure, map output, missing GPS,
and missing files. No separate production change is needed.

- [ ] **Step 1: Run the image info tests with warnings as errors**

Run:

```bash
uv run pytest tests/test_image_info.py -q -W error
```

Expected: all tests pass without warnings.

## Task 4: Viewer Fixes and Tests

**Files:**
- Modify: `src/custom_image_viewer/image_viewer.py`
- Create: `tests/test_image_viewer.py`

- [ ] **Step 1: Write the failing viewer tests**

Create `tests/test_image_viewer.py`:

```python
from pathlib import Path
from unittest.mock import MagicMock

from PIL import Image

from custom_image_viewer import image_viewer
from custom_image_viewer.image_viewer import ImageViewer


def make_viewer():
    viewer = ImageViewer.__new__(ImageViewer)
    viewer.master = MagicMock()
    viewer.image_list = []
    viewer.current_index = 0
    return viewer


def test_is_image_accepts_supported_files(tmp_path):
    viewer = make_viewer()
    image = tmp_path / "photo.PNG"
    image.write_bytes(b"")
    text = tmp_path / "notes.txt"
    text.write_text("x")

    assert viewer.is_image(image) is True
    assert viewer.is_image(text) is False
    assert viewer.is_image(tmp_path) is False


def test_image_path_clamps_index_and_handles_empty():
    viewer = make_viewer()
    viewer.image_list = [Path("a.png"), Path("b.jpg")]
    viewer.current_index = 5
    assert viewer.image_path == Path("b.jpg")
    assert viewer.current_index == 1

    viewer.image_list = []
    assert viewer.image_path is None


def test_resize_image_landscape_portrait_and_square():
    viewer = make_viewer()
    viewer.master.winfo_width.return_value = 200

    landscape = viewer.resize_image(Image.new("RGB", (400, 200)))
    portrait = viewer.resize_image(Image.new("RGB", (200, 400)))
    square = viewer.resize_image(Image.new("RGB", (200, 200)))

    assert landscape.size == (200, 100)
    assert portrait.size == (100, 200)
    assert square.size == (200, 200)


def test_load_image_populates_folder(tmp_path, monkeypatch):
    viewer = make_viewer()
    first = tmp_path / "a.png"
    first.write_bytes(b"")
    second = tmp_path / "b.jpg"
    second.write_bytes(b"")
    viewer.display_image = MagicMock()
    viewer.close_info_window = MagicMock()
    monkeypatch.setattr(
        image_viewer.filedialog,
        "askopenfilename",
        lambda **_: str(first),
    )

    viewer.load_image()

    assert viewer.image_folder == tmp_path
    assert viewer.current_index == 0
    assert set(viewer.image_list) == {first, second}
    viewer.display_image.assert_called_once()
    viewer.close_info_window.assert_called_once()


def test_load_image_accepts_unsupported_extension(tmp_path, monkeypatch):
    viewer = make_viewer()
    selected = tmp_path / "notes.txt"
    selected.write_text("x")
    viewer.display_image = MagicMock()
    viewer.close_info_window = MagicMock()
    monkeypatch.setattr(
        image_viewer.filedialog,
        "askopenfilename",
        lambda **_: str(selected),
    )

    viewer.load_image()

    assert viewer.image_list == [selected]
    assert viewer.current_index == 0


def test_navigation_calls_display_and_closes_info():
    viewer = make_viewer()
    viewer.image_list = [Path("a.png"), Path("b.png")]
    viewer.current_index = 1
    viewer.display_image = MagicMock()
    viewer.close_info_window = MagicMock()

    viewer.show_previous_image()
    assert viewer.current_index == 0
    viewer.show_next_image()
    assert viewer.current_index == 1
    assert viewer.display_image.call_count == 2
    assert viewer.close_info_window.call_count == 2


def test_status_bar_and_nav_state():
    viewer = make_viewer()
    viewer.status_bar = MagicMock()
    viewer.prev_button = MagicMock()
    viewer.next_button = MagicMock()
    viewer.image_list = [Path("a.png"), Path("b.png")]

    viewer.current_index = 0
    viewer.update_status_bar()
    viewer.update_nav_button_state()
    viewer.status_bar.config.assert_called_with(text="Image 1 of 2")
    viewer.prev_button.config.assert_called_with(state=image_viewer.tk.DISABLED)
    viewer.next_button.config.assert_called_with(state=image_viewer.tk.NORMAL)

    viewer.current_index = 1
    viewer.update_nav_button_state()
    viewer.prev_button.config.assert_called_with(state=image_viewer.tk.NORMAL)
    viewer.next_button.config.assert_called_with(state=image_viewer.tk.DISABLED)


def test_toggle_fullscreen_updates_attribute_and_menu():
    viewer = make_viewer()
    viewer.view_menu = MagicMock()
    viewer.master.attributes.return_value = False

    viewer.toggle_fullscreen()

    viewer.master.attributes.assert_any_call("-fullscreen", True)
    viewer.view_menu.entryconfig.assert_called_with(
        0, label="Exit Full Screen"
    )


def test_exit_fullscreen_turns_it_off():
    viewer = make_viewer()
    viewer.view_menu = MagicMock()
    viewer.master.attributes.return_value = True

    viewer.exit_fullscreen()

    viewer.master.attributes.assert_called_with("-fullscreen", False)
    viewer.view_menu.entryconfig.assert_called_with(0, label="Full Screen")


def test_show_about_dialog(monkeypatch):
    viewer = make_viewer()
    called = []
    monkeypatch.setattr(
        image_viewer.messagebox,
        "showinfo",
        lambda title, text: called.append((title, text)),
    )

    viewer.show_about_dialog()

    assert called
    assert called[0][0] == "About"


def test_add_and_remove_info_menu(monkeypatch):
    viewer = make_viewer()
    viewer.menu_bar = MagicMock()
    viewer.info_menu = None
    viewer.is_info_menu_open = False
    monkeypatch.setattr(image_viewer.tk, "Menu", lambda *args, **kwargs: MagicMock())

    viewer.add_info_menu()
    assert viewer.is_info_menu_open is True

    viewer.remove_info_menu()
    assert viewer.is_info_menu_open is False
    viewer.menu_bar.delete.assert_called_with("Info")


def test_display_image_without_images_returns():
    viewer = make_viewer()
    viewer.image_list = []
    viewer.current_index = 0
    viewer.display_image()


def test_display_image_loads_and_sizes(tmp_path, monkeypatch):
    viewer = make_viewer()
    path = tmp_path / "photo.png"
    Image.new("RGB", (400, 200), "red").save(path)
    viewer.image_list = [path]
    viewer.current_index = 0
    viewer.image_label = MagicMock()
    viewer.master.winfo_width.return_value = 100
    viewer.update_status_bar = MagicMock()
    viewer.update_nav_button_state = MagicMock()
    viewer.show_nav_buttons = MagicMock()
    viewer.add_info_menu = MagicMock()
    monkeypatch.setattr(image_viewer, "ImageTk", MagicMock())

    viewer.display_image()

    viewer.image_label.config.assert_called_once()
    viewer.update_status_bar.assert_called_once()
    viewer.update_nav_button_state.assert_called_once()
    viewer.show_nav_buttons.assert_called_once()
    viewer.add_info_menu.assert_called_once()
```

- [ ] **Step 2: Run the tests and verify they fail**

Run:

```bash
uv run pytest tests/test_image_viewer.py -q
```

Expected: FAIL because `exit_fullscreen` does not exist and the guards are missing.

- [ ] **Step 3: Update `image_viewer.py`**

Change the imports:

```python
from tkinter import filedialog, messagebox
```

Remove the unused `configure_logging` import from the `.config` import block and
add `APP_VERSION` so the About dialog can use the real version.

Add the missing bindings next to the existing ones:

```python
        self.master.bind("<Left>", lambda event: self.show_previous_image())
        self.master.bind("<Right>", lambda event: self.show_next_image())
        self.master.bind("<F11>", lambda event: self.toggle_fullscreen())
        self.master.bind("<Control-o>", lambda event: self.load_image())
        self.master.bind("<Escape>", lambda event: self.exit_fullscreen())
```

Replace `image_path`:

```python
    @property
    def image_path(self):
        if not self.image_list:
            return None
        self.current_index = max(
            0, min(self.current_index, len(self.image_list) - 1)
        )
        return self.image_list[self.current_index]
```

Add `exit_fullscreen` and update `toggle_fullscreen`:

```python
    def toggle_fullscreen(self):
        current_state = self.master.attributes("-fullscreen")
        next_state = not current_state

        label_text = "Exit Full Screen" if not current_state else "Full Screen"
        self.view_menu.entryconfig(0, label=label_text)
        self.master.attributes("-fullscreen", next_state)
        if self.image_path:
            self.display_image()

    def exit_fullscreen(self):
        if not self.master.attributes("-fullscreen"):
            return
        self.master.attributes("-fullscreen", False)
        self.view_menu.entryconfig(0, label="Full Screen")
        if self.image_path:
            self.display_image()
```

Replace `show_about_dialog`:

```python
    def show_about_dialog(self):
        about_text = (
            f"Image Viewer App\nVersion {APP_VERSION}\n\n© 2024 Image Viewer App"
        )
        messagebox.showinfo("About", about_text)
```

Replace `load_image`:

```python
    def load_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[
                (
                    "All Image Files",
                    "*.png *.jpg *.jpeg *.gif *.bmp *.webp",
                )
            ]
        )
        if not file_path:
            return
        file_path = Path(file_path)
        self.image_folder = file_path.parent
        self.image_list = sorted(
            (
                file
                for file in self.image_folder.glob("*")
                if self.is_image(file)
            ),
            key=lambda file: file.name.lower(),
        )
        try:
            self.current_index = self.image_list.index(file_path)
        except ValueError:
            self.image_list.append(file_path)
            self.current_index = len(self.image_list) - 1
        self.display_image()
        self.close_info_window()
```

Replace `display_image`:

```python
    def display_image(self):
        image_path = self.image_path
        if image_path is None:
            return
        try:
            image = Image.open(image_path)
        except (IOError, OSError, TypeError) as exc:
            logger.error("Error opening image: %s", exc)
            return
        image = self.resize_image(image)
        self.image = ImageTk.PhotoImage(image)
        self.image_label.config(image=self.image)
        self.update_status_bar()
        self.update_nav_button_state()
        self.show_nav_buttons()
        self.add_info_menu()
```

- [ ] **Step 4: Run the viewer tests**

Run:

```bash
uv run pytest tests/test_image_viewer.py -q
```

Expected: all viewer tests pass.

---

## Task 5: Entry Point Test

**Files:**
- Create: `tests/test_main.py`

- [ ] **Step 1: Write the failing entry point test**

Create `tests/test_main.py`:

```python
from unittest.mock import MagicMock

from custom_image_viewer import main as main_module


def test_main_builds_window_and_starts_loop(monkeypatch):
    window = MagicMock()
    viewer = MagicMock()
    monkeypatch.setattr(main_module.ttk, "Window", lambda **kwargs: window)
    monkeypatch.setattr(main_module, "ImageViewer", lambda master: viewer)
    monkeypatch.setattr(
        main_module, "configure_logging", MagicMock()
    )

    main_module.main()

    viewer.master.mainloop.assert_called_once()
```

- [ ] **Step 2: Run the test and verify it fails or passes**

Run:

```bash
uv run pytest tests/test_main.py -q
```

Expected: PASS if the current entry point behavior is unchanged. If it fails,
update `main.py` only to use `configure_logging()` and
`ImageViewer(ttk.Window(themename=AVAILABLE_THEMES[0]))`, preserving the current
behavior.

---

## Task 6: Documentation and Final Verification

**Files:**
- Replace: `README.md`
- Create: `CONTEXT.md`

- [ ] **Step 1: Replace `README.md`**

```markdown
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
```

- [ ] **Step 2: Create `CONTEXT.md`**

```markdown
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

## Known Limitations

- Geocoding requires network access and may be rate-limited.
- Map tiles are loaded by the browser, not bundled.
- Tests mock the GUI; there is no automated screenshot or visual regression test.
```

- [ ] **Step 3: Run the full verification**

Run:

```bash
uv sync --extra dev
uv run ruff check .
uv run ruff format --check .
uv run pytest
rm -rf data logs
uv run python -c "import custom_image_viewer.config"
test ! -d data && test ! -d logs
uv build
python3 -m zipfile -l dist/*.whl | grep custom_image_viewer/config.py
uv run python -c "from custom_image_viewer.main import main; print(callable(main))"
grep -R "eval(" src || true
```

Expected:

- Ruff and format checks pass.
- All tests pass.
- Importing config does not create `data/` or `logs/`.
- The wheel contains the package.
- `callable(main)` prints `True`.
- No `eval(` matches in `src`.

- [ ] **Step 4: Report status**

Summarize:

- Files changed.
- Test and lint results.
- Any unverified item, with the exact command needed to verify it.

Do not commit or push unless the user explicitly asks.

---

## Implementation Notes

Deviations made during execution:

- `configure_logging` uses `force=True` so repeated calls reconfigure the root
  logger cleanly.
- `ImageInfo.metadata` caches the first EXIF read per instance.
- `view_location_on_map` passes a string path to `folium.Map.save` for
  compatibility.
- `ImageInfo` accepts `None` and returns empty metadata for missing paths.
- The About dialog uses `APP_VERSION` instead of a hard-coded version.
- `ImageViewer.image_path` and `image_info` have return annotations to narrow
  types after the empty-list guard.
- The test suite has 44 tests. No `eval(` remains in `src`.

Post-review fixes:

- Empty and whitespace-only GPS components now raise and return `None`
  coordinates instead of placing the image at `(0, 0)`.
- `InfoWindow` computes coordinates once and calls geocoding only for the
  Location view. The map button is gated on coordinates, so it remains available
  when geocoding fails.
- Map output creation is wrapped and returns `None` on write or browser errors.
- `WM_DELETE_WINDOW` resets the info-window open flag, and `close_info_window`
  clears the reference.
- Added tests for whitespace GPS, Nominatim timeout/user agent, EXIF failure,
  map save failure, nested map output, main entry-point calls, shortcut
  bindings, and map-button behavior.
- `APP_VERSION` is `1.1.0`, and `.gitignore` now covers `dist/`, `build/`, and
  `*.egg-info/`.

