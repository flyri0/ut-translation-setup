import pathlib
from PIL import ImageTk, Image
from tkinter import ttk

from tkhtmlview import RenderHTML, HTMLLabel

from pages.base import BasePage

# TODO: Literally everything, this is just a test :_)
class WelcomePage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        controller.logger.debug("WelcomePage: loaded")
        controller.back_button.configure(state="disabled")
        self._display_banner()
        self._display_message()

        self.rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

    def _display_message(self):
        html_file = pathlib.Path(__file__).parent.parent / "assets" / "welcome_message.html"

        if html_file.exists():
            self.controller.logger.debug(f"WelcomePage: Welcome message successfully loaded from {html_file}")
            self.welcome_message = HTMLLabel(self, html=RenderHTML(html_file), cursor="arrow")
            self.welcome_message.grid(row=0, column=1, sticky="s", padx=10)
        else:
            self.controller.logger.warning(f"WelcomePage: Failed to load welcome message from {html_file}")
            self.welcome_message = ttk.Label(self, text="Until Then... em português!")
            self.welcome_message.grid(row=0, column=1, sticky="nsew")

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
