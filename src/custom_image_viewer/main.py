import ttkbootstrap as ttk
from .image_viewer import ImageViewer
from .config import configure_logging, AVAILABLE_THEMES


def main():
    """
    Main function to run the Image Viewer application.
    """
    configure_logging()
    app = ImageViewer(ttk.Window(themename=AVAILABLE_THEMES[0]))
    app.master.mainloop()


if __name__ == "__main__":
    main()
