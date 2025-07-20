import gettext
import pathlib
from PIL import ImageTk, Image
import ttkbootstrap as ttk

from pages.base import BasePage

# TODO: Implement i18n support
_ = gettext.gettext

class WelcomePage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        controller.logger.debug("WelcomePage: loaded")
        controller.title(_("Translation Installer: Welcome"))
        controller.back_button.configure(state="disabled", cursor="arrow")
        controller.next_button.configure(state="enabled", cursor="hand2")

        self._display_banner()
        self._display_message()

        self.rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

    def _display_message(self):
        def update_wraplength(event):
            message_label.config(wraplength=container.winfo_width() - 30)

        bold_font = ("TkDefaultFont", 12, "bold")
        italic_font = ("TkDefaultFont", 9, "italic")

        container = ttk.Frame(self)
        container.grid(row=0, column=1, sticky="nsew")

        for i in (0, 6):
            container.rowconfigure(i, weight=1)
        for i in range(1, 6):
            container.rowconfigure(i, weight=0)
        container.columnconfigure(0, weight=1)

        ttk.Label(container, text=_("Until Then... in portuguese!"), font=bold_font) \
            .grid(row=1, column=0, pady=(0, 10), sticky="n")

        message_label = ttk.Label(
            container,
            text=_(
                "Thank you for being here. This translation was made with love by fans, "
                "so that more people can experience the story of Until Then in our language. "
                "We hope you get as emotional as we did."
            )
        )
        message_label.grid(row=2, column=0, sticky="n")
        message_label.bind("<Configure>", update_wraplength)

        ttk.Label(container, text=_("Translation by: someone"), font=italic_font) \
            .grid(row=4, column=0, pady=(30, 0), sticky="s")

        ttk.Label(container, text=_("Installer by: someone"), font=italic_font) \
            .grid(row=5, column=0, sticky="s")

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

            self.banner_label = ttk.Label(self, image=self.banner, borderwidth=0) # type: ignore
            self.banner_label.grid(row=0, column=0, sticky="nsew")
