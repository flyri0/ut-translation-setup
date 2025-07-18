import os
import pathlib
import platform
import tkinter.ttk as ttk

from pages.base import BasePage

# TODO: Everything
class SelectGamePathPage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        controller.logger.debug("SelectGamePathPage: loaded")
        controller.back_button.configure(state="enabled")

        selected_path_frame = ttk.Frame(self)
        selected_path_frame.pack(fill="x", expand=True, padx=100)
        selected_path_frame.columnconfigure(0, weight=1)

        self.path_label = ttk.Label(selected_path_frame, borderwidth=1, relief="groove")
        self.path_label.grid(row=0, column=0, sticky="ew", ipady=2)

        self.select_path_button = ttk.Button(selected_path_frame, text="Selecionar")
        self.select_path_button.grid(row=0, column=1, padx=(10, 0))

        self.status_label = ttk.Label(selected_path_frame)
        self.status_label.grid(row=1, column=0, columnspan=2, sticky="w")

    def _get_steam_path(self):
        system = platform.system()

        match system:
            case "Windows":
                possible_paths = [
                    pathlib.Path.home() / "AppData" / "Local" / "Steam" / "steamapps",
                    pathlib.Path(os.environ.get("ProgramFiles(x86)")) / "Steam" / "steamapps",
                    pathlib.Path(os.environ.get("ProgramFiles")) / "Steam" / "steamapps",
                ]
            case "Linux":
                possible_paths = [
                    pathlib.Path.home() / ".steam" / "steam" / "steamapps",
                    pathlib.Path.home() / ".local" / "share" / "Steam" / "steamapps",
                ]
            case "Darwin":
                possible_paths = [
                    pathlib.Path.home() / "Library" / "Application Support" / "Steam" / "steamapps"
                ]
            case _:
                self.controller.logger.warning(f"SelectGamePathPage: Unsupported system: {system}")
                return None

        for path in possible_paths:
            if path.exists():
                self.controller.logger.debug(f"SelectGamePathPage: Steam path found at {path}")
                return path.resolve()

        self.controller.logger.info("SelectGamePathPage: Steam not found in standard directories")
        return None