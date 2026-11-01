import logging
from pathlib import Path

from custom_image_viewer import config


def test_data_dir_default(monkeypatch):
    monkeypatch.delenv("IMAGE_VIEWER_DATA_DIR", raising=False)
    assert config.get_data_dir() == (Path.home() / ".local" / "share" / "image-viewer")


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
