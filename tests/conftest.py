import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


@pytest.fixture(autouse=True)
def isolate_runtime_dirs(monkeypatch, tmp_path):
    monkeypatch.setenv("IMAGE_VIEWER_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("IMAGE_VIEWER_LOG_DIR", str(tmp_path / "logs"))
