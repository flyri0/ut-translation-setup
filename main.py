import gettext
import pathlib
import tkinter.messagebox

import darkdetect
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from typing import Type, Optional

from screeninfo import get_monitors

from logger import _Logger
from pages.base import BasePage
from pages.select_game_path import SelectGamePathPage
from pages.welcome import WelcomePage
from state import AppState

page_sequence: list[Type[BasePage]] = [
    WelcomePage,
    SelectGamePathPage,
]

# TODO: Implement i18n support
_ = gettext.gettext

LOG_PREFIX = "App:"

class App(ttk.Window):
    def __init__(self, theme_name: str = "cosmo"):
        super().__init__(themename=theme_name)

        self.report_callback_exception = self._handle_exception
        self.protocol("WM_DELETE_WINDOW", self._handle_exit)

        self.state = AppState()
        self.logger = _Logger.get_logger()
        self.logger.info(f"{LOG_PREFIX} Initialized")

        self._center_window()
        self._set_icon()
        self.title(_("Until Then - Install Translation"))

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.container = ttk.Frame(self)
        self.container.grid(row=0, column=0, sticky="nsew")
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        controls_container = ttk.Frame(self)
        controls_container.grid(row=1, column=0, sticky="ew")
        controls_container.grid_columnconfigure(0, weight=1)

        ttk.Separator(controls_container, orient="horizontal", style=SECONDARY).grid(row=0, column=0, columnspan=3, sticky="ew")

        self.cancel_button = ttk.Button(
            controls_container,
            text=_("Cancel"),
            style=f'{OUTLINE},{DANGER}',
            cursor="hand2",
            command=lambda: self._handle_exit())
        self.cancel_button.grid(row=1, column=0, sticky="w", pady=10, padx=(10, 0))

        self.back_button = ttk.Button(
            controls_container,
            text=_("Back"),
            style=OUTLINE,
            cursor="hand2",
            command=lambda: self._show_page(self.current_index - 1))
        self.back_button.grid(row=1, column=1, sticky="w", pady=10, padx=(0, 10))

        self.next_button = ttk.Button(
            controls_container,
            text=_("Next"),
            style=OUTLINE,
            cursor="hand2",
            command=lambda: self._show_page(self.current_index + 1))
        self.next_button.grid(row=1, column=2, sticky="e", pady=10, padx=(0, 10))

        self.page_sequence = page_sequence
        self.current_index: int = 0
        self.current_page: Optional[ttk.Frame] = None
        self._show_page(0)

    def _show_page(self, index: int):
        if not (0 <= index < len(self.page_sequence)):
            self.logger.warning(f"{LOG_PREFIX} Page index {index} out of bounds")
            return

        if self.current_page is not None:
            self.logger.debug(f"{LOG_PREFIX} Destroying page {type(self.current_page).__name__}")
            self.current_page.destroy()

        page_class = self.page_sequence[index]
        page = page_class(parent=self.container, controller=self)
        page.grid(row=0, column=0, sticky="nsew")
        self.current_page = page
        self.current_index = index

        self.logger.info(f"{LOG_PREFIX} Page {type(page).__name__} displayed")

    def _set_icon(self):
        icon_path = pathlib.Path(__file__).parent / "assets" / "icon.ico"

        try:
            self.iconbitmap(default=str(icon_path))
            self.iconbitmap(str(icon_path))
            self.logger.debug(f"{LOG_PREFIX} Icon set from {icon_path}")
        except Exception as error:
            self.logger.warning(f"{LOG_PREFIX} Failed to set icon from {icon_path}: {error}")

    def _center_window(self):
        screen_width, screen_height = None, None
        for monitor in get_monitors():
            if monitor.is_primary:
                screen_width = monitor.width
                screen_height = monitor.height
                self.logger.debug(f"{LOG_PREFIX} Primary monitor detected: {monitor.name} with dimensions {monitor.width}x{monitor.height}")
                break

        window_width = int(screen_width * 0.4)
        window_height = int(screen_height * 0.5)
        position_x = int(screen_width - window_width) // 2
        position_y = int(screen_height - window_height) // 2

        self.logger.debug(f"{LOG_PREFIX} Window size set to {window_width}x{window_height} at ({position_x}, {position_y})")
        self.resizable(False, False)
        self.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")

    def _handle_exit(self):
        self.logger.info(f"{LOG_PREFIX} Termination requested by user")
        if tkinter.messagebox.askyesno(_("Exit"), _("Are you sure you want to exit?")):
            self.destroy()
        else:
            self.logger.info(f"{LOG_PREFIX} Termination aborted by user")

    def _handle_exception(self, exc_type, exc_value, exc_traceback):
        self.logger.error("Unhandled exception in Tkinter callback", exc_info=(exc_type, exc_value, exc_traceback))

        tkinter.messagebox.showerror(
            _("An unexpected error has occurred"),
            f"A log file was generated at: {AppLogger.get_log_file_path()}"
        )

        self.destroy()

if __name__ == "__main__":
    logger = _Logger.get_logger()
    theme = "litera"

    try:
        if darkdetect.isDark():
            logger.info(f"{LOG_PREFIX} Dark mode detected")
            theme = "darkly"

        app = App(theme_name=theme)
        app.mainloop()
    except Exception:
        # Only handles setup/startup errors now
        logger.exception("Unhandled exception occurred during runtime")
        tkinter.messagebox.showerror(
            _("An unexpected error has occurred"),
            f"A log file was generated at: {AppLogger.get_log_file_path()}"
        )
    finally:
        logger.info(f"{LOG_PREFIX} Terminated")