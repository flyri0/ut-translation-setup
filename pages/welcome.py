import pathlib
from PIL import ImageTk, Image
from tkinter import ttk

from pages.base import BasePage

# TODO: Literally everything, this is just a test :_)
class WelcomePage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        controller.logger.debug("WelcomePage: loaded")
        self._display_banner()

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        label = ttk.Label(self, text="Bem-vindo ao UT-Translation")
        label.grid(row=0, column=1)

    def _display_banner(self):
        banner_path = pathlib.Path(__file__).parent.parent / "assets" / "banner.jpg"
        window_height = self.controller.winfo_height()

        try:
            banner_source = Image.open(banner_path)
            self.controller.logger.debug(f"WelcomePage: Banner image loaded from {banner_path}")
        except Exception as banner_path_error:
            self.controller.logger.warning(f"WelcomePage: Failed to load banner image from {banner_path}: {banner_path_error}")
            banner_source = None

        if banner_source is not None:
            aspect_ratio = banner_source.width / banner_source.height
            self.resized_banner_source = banner_source.resize(
                (
                    int(window_height * aspect_ratio),
                    window_height
                ),
                Image.Resampling.BILINEAR
            )
            self.banner = ImageTk.PhotoImage(self.resized_banner_source)

            self.banner_label = ttk.Label(self, image=self.banner) # type: ignore
            self.banner_label.grid(row=0, column=0, sticky="nsew")
