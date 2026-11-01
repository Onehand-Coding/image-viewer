from unittest.mock import MagicMock

from custom_image_viewer import main as main_module


def test_main_builds_window_and_starts_loop(monkeypatch):
    window = MagicMock()
    viewer = MagicMock()
    monkeypatch.setattr(main_module.ttk, "Window", lambda **kwargs: window)
    monkeypatch.setattr(main_module, "ImageViewer", lambda master: viewer)
    monkeypatch.setattr(main_module, "configure_logging", MagicMock())

    main_module.main()

    viewer.master.mainloop.assert_called_once()
