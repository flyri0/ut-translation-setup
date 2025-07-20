import gettext
import os
import pathlib
import platform

import vdf
from ttkbootstrap import ttk

from pages.base import BasePage

# TODO: Implement i18n support
_ = gettext.gettext

FULL_GAME_ID = 1574820
DEMO_GAME_ID = 2296400
LOG_PREFIX = "SelectGamePathPage:"

# TODO: Implement auto install path find logic
class SelectGamePathPage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        controller.logger.debug(f"{LOG_PREFIX} Loaded")
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

    def _detect_until_then_game_path(self):
        full_path = self._autodetect_game_path(FULL_GAME_ID)
        if full_path:
            self.controller.logger.info(f"{LOG_PREFIX} Full version of Until Then found")
            self.controller.state.game_path = full_path
            return

        self.controller.logger.info(f"{LOG_PREFIX} Full version not found, trying demo")
        demo_path = self._autodetect_game_path(DEMO_GAME_ID)
        if demo_path:
            self.controller.logger.info(f"{LOG_PREFIX} Demo version of Until Then found")
            self.controller.state.game_path = demo_path
        else:
            self.controller.logger.info(f"{LOG_PREFIX} Demo version not found")
            self.controller.state.game_path = None

    def _autodetect_game_path(self, game_id: int):
        self.controller.logger.debug(f"{LOG_PREFIX} Trying to auto-detect game path")

        steam_path = self._get_steam_path()
        library_folders_path = steam_path / "steamapps" / "libraryfolders.vdf"
        library_data = vdf.load(open(library_folders_path.resolve()))

        libraries = []

        if "libraryfolders" in library_data:
            folders = library_data["libraryfolders"]
            for key, entry in folders.items():
                # Steam 2023+: folders are dicts with 'path'
                if isinstance(entry, dict) and "path" in entry:
                    libraries.append(pathlib.Path(entry["path"]))
                # Older format: folders are direct paths
                elif isinstance(entry, str):
                    libraries.append(pathlib.Path(entry))
        else:
            libraries.append(steam_path)

        for library_path in libraries:
            manifest_path = library_path / "steamapps" / f"appmanifest_{game_id}.acf"
            if manifest_path.exists():
                self.controller.logger.debug(f"{LOG_PREFIX} Found manifest at {manifest_path}")
                manifest = vdf.load(open(manifest_path.resolve()))
                install_dir = manifest["AppState"]["installdir"]
                game_path = library_path / "steamapps" / "common" / install_dir
                if game_path.exists():
                    self.controller.logger.debug(f"{LOG_PREFIX} Found game at {game_path}")
                    return game_path.resolve()

        self.controller.logger.warning(f"{LOG_PREFIX} Could not auto-detect path for game ID {game_id}")
        return None

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
                self.controller.logger.warning(f"{LOG_PREFIX} Unsupported system: {system}")
                return None

        for path in possible_paths:
            if path.exists():
                self.controller.logger.debug(f"{LOG_PREFIX} Steam path found at {path}")
                return path.resolve()

        self.controller.logger.info(f"{LOG_PREFIX} Steam not found in standard directories")
        return None