import gettext
import os
import pathlib
import platform

from ttkbootstrap import ttk

from pages.base import BasePage

# TODO: Implement i18n support
_ = gettext.gettext

# TODO: Implement auto install path find logic
class SelectGamePathPage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        controller.logger.debug("SelectGamePathPage: Loaded")
        controller.title(_("Translation Installer: Find Game Install Directory"))
        controller.back_button.configure(state="enabled", cursor="hand2")
        controller.next_button.configure(state="disabled", cursor="arrow")

        container = ttk.Frame(self)
        container.pack(fill="x", expand=True, padx=100)
        container.columnconfigure(0, weight=1)

        path_frame = ttk.LabelFrame(container, text=_("Selected Directory"))
        path_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 5))

        self.path_label = ttk.Label(path_frame)
        self.path_label.pack(fill="x", expand=True, ipady=2, padx=5, pady=5)

        self.select_path_button = ttk.Button(container, text=_("Select"))
        self.select_path_button.grid(row=1, column=1, padx=(10, 0), sticky="e")

        self.status_label = ttk.Label(container)
        self.status_label.grid(row=1, column=0, sticky="w", pady=(5, 0))


    def _get_steam_path(self):
        system = platform.system()

        match system:
            case "Windows":
                possible_paths = [
                    pathlib.Path(os.environ.get("ProgramFiles(x86)")) / "Steam",
                    pathlib.Path(os.environ.get("ProgramFiles")) / "Steam",
                ]
            case "Linux":
                possible_paths = [
                    pathlib.Path.home() / ".steam" / "steam",
                    pathlib.Path.home() / ".local" / "share" / "Steam",
                    pathlib.Path.home() / ".var" / "app" / "com.valvesoftware.Steam" / "data" / "Steam"
                ]
            case "Darwin":
                possible_paths = [
                    pathlib.Path.home() / "Library" / "Application Support" / "Steam"
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