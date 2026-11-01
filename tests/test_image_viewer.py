from pathlib import Path
from unittest.mock import MagicMock

from PIL import Image

from custom_image_viewer import image_viewer
from custom_image_viewer.image_viewer import ImageViewer, InfoWindow


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
    viewer.view_menu.entryconfig.assert_called_with(0, label="Exit Full Screen")


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


def test_shortcuts_are_bound(monkeypatch):
    master = MagicMock()
    monkeypatch.setattr(image_viewer.ttk, "Label", lambda *args, **kwargs: MagicMock())
    monkeypatch.setattr(image_viewer.ttk, "Frame", lambda *args, **kwargs: MagicMock())
    monkeypatch.setattr(image_viewer.tk, "Menu", lambda *args, **kwargs: MagicMock())
    monkeypatch.setattr(image_viewer.tk, "Button", lambda *args, **kwargs: MagicMock())

    ImageViewer(master)

    bound = {call.args[0] for call in master.bind.call_args_list}
    assert {"<Left>", "<Right>", "<F11>", "<Control-o>", "<Escape>"} <= bound


def test_info_window_shows_map_button_without_address(monkeypatch):
    window = InfoWindow.__new__(InfoWindow)
    window.image_info = MagicMock()
    window.info_needed = "Location"
    window.coordinates = (1.0, 2.0)
    window.address = None
    frame = MagicMock()
    text = MagicMock()
    button = MagicMock()
    monkeypatch.setattr(image_viewer.ttk, "Frame", lambda *args, **kwargs: frame)
    monkeypatch.setattr(image_viewer.ttk, "Text", lambda *args, **kwargs: text)
    monkeypatch.setattr(image_viewer.ttk, "Button", MagicMock(return_value=button))

    window.create_widgets()

    button.pack.assert_called_once()
    text.insert.assert_called_once()


def test_info_window_hides_map_button_without_coordinates(monkeypatch):
    window = InfoWindow.__new__(InfoWindow)
    window.image_info = MagicMock()
    window.info_needed = "Location"
    window.coordinates = None
    window.address = None
    frame = MagicMock()
    text = MagicMock()
    button_factory = MagicMock()
    monkeypatch.setattr(image_viewer.ttk, "Frame", lambda *args, **kwargs: frame)
    monkeypatch.setattr(image_viewer.ttk, "Text", lambda *args, **kwargs: text)
    monkeypatch.setattr(image_viewer.ttk, "Button", button_factory)

    window.create_widgets()

    button_factory.assert_not_called()


def test_close_info_window_clears_reference():
    viewer = make_viewer()
    info_window = MagicMock()
    info_window.is_open = True
    viewer.info_window = info_window

    viewer.close_info_window()

    info_window.destroy.assert_called_once()
    assert viewer.info_window is None


def test_info_window_close_resets_flag():
    window = InfoWindow.__new__(InfoWindow)
    window.is_open = True
    window.destroy = MagicMock()

    window._on_close()

    assert window.is_open is False
    window.destroy.assert_called_once()


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
