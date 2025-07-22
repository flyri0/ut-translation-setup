import gettext
import os
import pathlib
import platform
import tkinter.filedialog
import tkinter.messagebox

import vdf
from ttkbootstrap import ttk, DANGER

from pages.base import BasePage

_ = gettext.gettext

FULL_GAME_ID = 1574820
DEMO_GAME_ID = 2296400
GAME_EXE_NAME = "UntilThen.exe"
LOG_PREFIX = "SelectGamePathPage:"


class SelectGamePathPage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        self.controller.logger.debug(f"{LOG_PREFIX} Loaded")
        self.controller.title(_("Translation Installer: Find Game Install Directory"))

        container = ttk.Frame(self)
        container.pack(fill="x", expand=True, padx=100)
        container.columnconfigure(0, weight=1)

        path_frame = ttk.LabelFrame(container, text=_("Selected Path"))
        path_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 5))

        self.path_label = ttk.Label(path_frame)
        self.path_label.pack(fill="x", expand=True, ipady=2, padx=5, pady=5)

        self.select_path_button = ttk.Button(
            container, text=_("Select"), command=self._handle_select
        )
        self.select_path_button.grid(row=1, column=1, padx=(10, 0), sticky="e")

        self.status_label = ttk.Label(container, font=("TkDefaultFont", 8, "bold"))
        self.status_label.grid(row=1, column=0, sticky="w", pady=(5, 0))

        self._detect_until_then_game_path()
        self.after_idle(self._validate_path) # type: ignore

    def _validate_path(self):
        game_path = self.controller.state.game_path

        exe_path = game_path / GAME_EXE_NAME if game_path else None

        if not exe_path or not exe_path.is_file():
            self.controller.logger.warning(f"{LOG_PREFIX} Valid game executable not found at {exe_path}")
            self.status_label.configure(text=_("UntilThen.exe not found."), style="danger.TLabel")
            self.controller.next_button.configure(state="disabled", cursor="arrow")
            tkinter.messagebox.showwarning(
                _("Game executable not found"),
                _("We couldn't find UntilThen.exe. Please select the correct game folder."),
            )
        else:
            self.controller.logger.info(f"{LOG_PREFIX} Valid game executable found at {exe_path}")
            self.path_label.configure(text=str(exe_path))
            self.status_label.configure(text=_("UntilThen.exe found."), style="success.TLabel")
            self.controller.next_button.configure(state="enabled", cursor="hand2")

    def _detect_until_then_game_path(self):
        if self.controller.state.game_path is not None:
            return

        for game_id in [FULL_GAME_ID, DEMO_GAME_ID]:
            path = self._autodetect_game_path(game_id)
            if path:
                self.controller.logger.info(f"{LOG_PREFIX} Game found for ID {game_id}")
                self.controller.state.game_path = path
                self.controller.state.is_demo = (game_id == DEMO_GAME_ID)
                return

        self.controller.logger.info(f"{LOG_PREFIX} No game installation found")
        self.controller.state.game_path = None

    def _handle_select(self):
        selected_path = tkinter.filedialog.askopenfilename(
            filetypes=[(_("Game executable file"), "*.exe")]
        )
        if selected_path:
            self.path_label.configure(text=str(selected_path))
            self.controller.state.game_path = pathlib.Path(selected_path).parent
        self._validate_path()

    def _autodetect_game_path(self, game_id: int):
        self.controller.logger.debug(f"{LOG_PREFIX} Trying to auto-detect game path for ID {game_id}")

        steam_path = self._get_steam_path()
        if not steam_path:
            return None

        library_folders_path = steam_path / "steamapps" / "libraryfolders.vdf"
        try:
            with open(library_folders_path, encoding="utf-8") as f:
                library_data = vdf.load(f)
        except FileNotFoundError:
            self.controller.logger.warning(f"{LOG_PREFIX} libraryfolders.vdf not found")
            return None

        libraries = []
        folders = library_data.get("libraryfolders", {})
        for entry in folders.values():
            if isinstance(entry, dict) and "path" in entry:
                libraries.append(pathlib.Path(entry["path"]))
            elif isinstance(entry, str):
                libraries.append(pathlib.Path(entry))

        if not libraries:
            libraries.append(steam_path)

        for library_path in libraries:
            manifest_path = library_path / "steamapps" / f"appmanifest_{game_id}.acf"
            if manifest_path.exists():
                try:
                    with open(manifest_path, encoding="utf-8") as f:
                        manifest = vdf.load(f)
                    install_dir = manifest["AppState"]["installdir"]
                    game_path = library_path / "steamapps" / "common" / install_dir
                    if game_path.exists():
                        self.controller.logger.debug(f"{LOG_PREFIX} Found game at {game_path}")
                        return game_path.resolve()
                except Exception as e:
                    self.controller.logger.warning(f"{LOG_PREFIX} Failed to parse manifest: {e}")

        self.controller.logger.warning(f"{LOG_PREFIX} Could not auto-detect path for game ID {game_id}")
        return None

    def _get_steam_path(self):
        system = platform.system()

        if system == "Windows":
            possible_paths = [
                pathlib.Path(os.environ.get("ProgramFiles(x86)", "")) / "Steam",
                pathlib.Path(os.environ.get("ProgramFiles", "")) / "Steam",
            ]
        elif system == "Linux":
            home = pathlib.Path.home()
            possible_paths = [
                home / ".steam" / "steam",
                home / ".local" / "share" / "Steam",
                home / ".var" / "app" / "com.valvesoftware.Steam" / "data" / "Steam",
            ]
        else:
            self.controller.logger.warning(f"{LOG_PREFIX} Unsupported system: {system}")
            return None

        for path in possible_paths:
            if path.exists():
                self.controller.logger.debug(f"{LOG_PREFIX} Steam path found at {path}")
                return path.resolve()

        self.controller.logger.info(f"{LOG_PREFIX} Steam not found in standard directories")
        return None
