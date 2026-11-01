import ttkbootstrap as ttk

from .config import AVAILABLE_THEMES, configure_logging
from .image_viewer import ImageViewer


def main():
    """
    Main function to run the Image Viewer application.
    """
    configure_logging()
    app = ImageViewer(ttk.Window(themename=AVAILABLE_THEMES[0]))
    app.master.mainloop()


if __name__ == "__main__":
    main()
