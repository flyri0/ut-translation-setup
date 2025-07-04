import pathlib
import tkinter as tk
from typing import Literal, Dict

from screeninfo import get_monitors

from pages.welcome import WelcomePage
from pages.select_path import SelectPathPage

AvailablePages = Literal["WelcomePage", "SelectPathPage"]

class AppController(tk.Tk):
    def __init__(self):
        super().__init__()
        self._center_window()
        self._set_icon()
        self.title("Until Then - Instalar Tradução")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        container = tk.Frame(self)
        container.grid(row=0, column=0, sticky="nsew")


        self.pages: Dict[AvailablePages, tk.Frame] = {}
        for Page in (WelcomePage, SelectPathPage):
            name: AvailablePages = Page.__name__ # type: ignore
            page = Page(parent=container, controller=self)
            self.pages[name] = page
            page.grid(row=0, column=0, sticky="nsew")

        self.show_page("WelcomePage")

    def show_page(self, name: AvailablePages):
        page = self.pages[name]
        page.tkraise()

    def _center_window(self):
        screen_width, screen_height = None, None
        for monitor in get_monitors():
            if monitor.is_primary:
                screen_width = monitor.width
                screen_height = monitor.height
                break

        window_width = int(screen_width * 0.5)
        window_height = int(screen_height * 0.5)
        position_x = (screen_width - window_width) // 2
        position_y = (screen_height - window_height) // 2

        self.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")

    def _set_icon(self):
        icon_path = pathlib.Path(__file__).parent / "assets" / "icon.ico"
        self.iconbitmap(icon_path)

if __name__ == "__main__":
    app = AppController()
    app.mainloop()