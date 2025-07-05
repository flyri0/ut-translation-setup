import pathlib
import tkinter as tk
import tkinter.messagebox
from typing import Literal, Type, Optional, Dict

from screeninfo import get_monitors

from logger import AppLogger
from pages.base import BasePage
from pages.welcome import WelcomePage
from pages.select_path import SelectPathPage

# Keep this in sync with PageClassMap
AvailablePages = Literal["WelcomePage", "SelectPathPage"]
PagesClassMap: Dict[str, Type[BasePage]] = {
    "WelcomePage": WelcomePage,
    "SelectPathPage": SelectPathPage,
}

class AppController(tk.Tk):
    def __init__(self):
        super().__init__()
        self.logger = AppLogger.get_logger()
        self.logger.info("App initialized")
        self._center_window()
        self._set_icon()
        self.title("Until Then - Instalar Tradução")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.container = tk.Frame(self)
        self.container.grid(row=0, column=0, sticky="nsew")

        self.current_page: Optional[tk.Frame] = None
        self.show_page("WelcomePage")

    def show_page(self, name: AvailablePages):
        if name not in PagesClassMap:
            self.logger.error(f"Tried to navigate to unknown page: {name}")
            raise ValueError(f"Invalid page name: {name}")

        self.logger.info(f"Navigating to page: {name}")

        if self.current_page is not None:
            self.logger.debug(f"Destroying current page: {type(self.current_page).__name__}")
            self.current_page.destroy()

        page_class: Type[tk.Frame] = PagesClassMap[name]
        page = page_class(parent=self.container, controller=self)
        self.logger.debug(f"Instantiated page: {type(page).__name__}")
        page.grid(row=0, column=0, sticky="nsew")

        self.current_page = page

    def _center_window(self):
        screen_width, screen_height = None, None
        for monitor in get_monitors():
            if monitor.is_primary:
                screen_width = monitor.width
                screen_height = monitor.height
                self.logger.debug(f"Primary monitor detected: {screen_width}x{screen_height}")
                break

        window_width = int(screen_width * 0.5)
        window_height = int(screen_height * 0.5)
        position_x = (screen_width - window_width) // 2
        position_y = (screen_height - window_height) // 2

        self.logger.debug(f"Window size set to {window_width}x{window_height} at ({position_x}, {position_y})")
        self.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")

    def _set_icon(self):
        icon_path = pathlib.Path(__file__).parent / "assets" / "icon.ico"
        try:
            self.iconbitmap(icon_path)
            self.logger.debug(f"Application icon set from {icon_path}")
        except Exception as icon_error:
            self.logger.warning(f"Failed to set application icon: {icon_error}")

if __name__ == "__main__":
    try:
        app = AppController()
        app.mainloop()
    except Exception as e:
        logger = AppLogger.get_logger()
        logger.exception("Unhandled exception occurred during runtime")

        tk.messagebox.showerror("Ocorreu um erro inesperado", f"Um arquivo de log foi gerado em: {AppLogger.get_log_file_path()}")
    finally:
        logger = AppLogger.get_logger()
        logger.info("Application closed")