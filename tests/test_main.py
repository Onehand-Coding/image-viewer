from unittest.mock import MagicMock

from custom_image_viewer import main as main_module


def test_main_builds_window_and_starts_loop(monkeypatch):
    window = MagicMock()
    viewer = MagicMock()
    window_factory = MagicMock(return_value=window)
    viewer_factory = MagicMock(return_value=viewer)
    logging_mock = MagicMock()
    monkeypatch.setattr(main_module.ttk, "Window", window_factory)
    monkeypatch.setattr(main_module, "ImageViewer", viewer_factory)
    monkeypatch.setattr(main_module, "configure_logging", logging_mock)

    main_module.main()

    logging_mock.assert_called_once()
    window_factory.assert_called_once_with(themename=main_module.AVAILABLE_THEMES[0])
    viewer_factory.assert_called_once_with(window)
    viewer.master.mainloop.assert_called_once()
