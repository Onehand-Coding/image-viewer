from __future__ import annotations

import logging
import os
from pathlib import Path

APP_NAME = "Image Viewer"
APP_VERSION = "1.1.0"
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
