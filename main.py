import pathlib
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox
from typing import Type, Optional

from screeninfo import get_monitors

from logger import AppLogger
from pages.base import BasePage
from pages.welcome import WelcomePage
from pages.select_game_path import SelectGamePathPage

# Single source of truth: ordered page classes
page_sequence: list[Type[BasePage]] = [
    WelcomePage,
    SelectGamePathPage,
]


class AppController(tk.Tk):
    def __init__(self):
        super().__init__()
        self.protocol("WM_DELETE_WINDOW", self._handle_exit)
        self.logger = AppLogger.get_logger()
        self.logger.info("Application initialized")

        self._center_window()
        self._set_icon()
        self.title("Until Then - Instalar Tradução")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.container = tk.Frame(self)
        self.container.grid(row=0, column=0, sticky="nsew")
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        controls_container = ttk.Frame(self)
        controls_container.grid(row=1, column=0, sticky="ew")
        controls_container.grid_columnconfigure(0, weight=1)

        ttk.Separator(controls_container, orient="horizontal").grid(row=0, column=0, columnspan=3, sticky="ew")

        self.back_button = ttk.Button(controls_container, text="Voltar", command=lambda: self.previous_page())
        self.back_button.grid(row=1, column=0, sticky="w", padx=5, pady=5)

        self.next_button = ttk.Button(controls_container, text="Próximo", command=lambda: self.next_page())
        self.next_button.grid(row=1, column=2, sticky="e", padx=5, pady=5)

        self.cancel_button = ttk.Button(controls_container, text="Cancelar", command=lambda: self._handle_exit())
        self.cancel_button.grid(row=1, column=1, sticky="e", padx=5, pady=5)

        self.page_sequence = page_sequence
        self.current_index: int = 0
        self.current_page: Optional[tk.Frame] = None

        self._show_page_by_index(self.current_index)

    def _show_page_by_index(self, index: int):
        if 0 <= index < len(self.page_sequence):
            self.current_index = index
            page_class = self.page_sequence[index]
            self._show_page_instance(page_class)
            self.logger.info(f"Page \"{page_class.__name__}\" displayed")
        else:
            self.logger.warning(f"Index out of bounds: {index}")

    def next_page(self):
        if self.current_index < len(self.page_sequence) - 1:
            self._show_page_by_index(self.current_index + 1)

    def previous_page(self):
        if self.current_index > 0:
            self._show_page_by_index(self.current_index - 1)

    def _handle_exit(self):
        if tk.messagebox.askyesno("Sair", "Tem certeza que deseja sair?"):
            self.logger.info("Terminated by the user")
            self.destroy()

    def _show_page_instance(self, page_class: Type[BasePage]):
        if self.current_page is not None:
            self.logger.debug(f"Destroying current page: {type(self.current_page).__name__}")
            self.current_page.destroy()

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

        window_width = int(screen_width * 0.4)
        window_height = int(screen_height * 0.5)
        position_x = (screen_width - window_width) // 2
        position_y = (screen_height - window_height) // 2

        self.logger.debug(f"Window size set to {window_width}x{window_height} at ({position_x}, {position_y})")
        self.resizable(False, False)
        self.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")

    def _set_icon(self):
        icon_path = pathlib.Path(__file__).parent / "assets" / "icon.ico"
        try:
            self.iconbitmap(str(icon_path))
            self.logger.debug(f"Application icon set from {icon_path}")
        except Exception as icon_error:
            self.logger.warning(f"Failed to set application icon: {icon_error}")

if __name__ == "__main__":
    logger = AppLogger.get_logger()
    try:
        app = AppController()
        app.mainloop()
    except Exception:
        logger.exception("Unhandled exception occurred during runtime")
        tk.messagebox.showerror(
            "Ocorreu um erro inesperado",
            f"Um arquivo de log foi gerado em: {AppLogger.get_log_file_path()}"
        )
    finally:
        logger.info("Application closed")
