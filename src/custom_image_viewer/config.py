import logging
from pathlib import Path
from typing import Tuple, List


def find_project_root() -> Path:
    """Find the project root directory by locating pyproject.toml."""
    current_path = Path(__file__).resolve()
    for parent in current_path.parents:
        if (parent / "pyproject.toml").exists():
            return parent
    raise FileNotFoundError("Could not find pyproject.toml in any parent directory")


# Directory setup
ROOT_DIR = find_project_root()
DATA_FOLDER = ROOT_DIR / "data"
LOGS_FOLDER = ROOT_DIR / "logs"

DATA_FOLDER.mkdir(exist_ok=True)
LOGS_FOLDER.mkdir(exist_ok=True)

# Logging configuration
LOG_FILE = LOGS_FOLDER / "image_viewer.log"
LOG_LEVEL = logging.INFO
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"


def configure_logging(*, log_level: int = LOG_LEVEL, log_file: Path = LOG_FILE) -> None:
    """Configure logging for the application.

    Args:
        log_level: Logging level (e.g., logging.INFO, logging.DEBUG).
        log_file: Path to the log file.
    """
    log_handlers = [logging.StreamHandler()]
    if log_file:
        log_handlers.append(logging.FileHandler(log_file, mode="w"))

    logging.basicConfig(
        level=log_level,
        handlers=log_handlers,
        format=LOG_FORMAT,
    )


# Application configuration
APP_NAME = "Image Viewer"
APP_VERSION = "1.1"
MASTER_SIZE = "500x550"
INFO_WINDOW_SIZE = "300x150"
INFO_WINDOW_ALT_SIZE = "200x100"
SUPPORTED_IMAGE_FORMATS: Tuple[str, ...] = (
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".bmp",
    ".webp",
)
AVAILABLE_THEMES: List[str] = ["darkly", "flatly", "litera"]

# Map view configuration
MAP_ZOOM_START = 15
MAP_POPUP_TEXT = "Image Location"
