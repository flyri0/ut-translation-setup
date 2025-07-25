import gettext
import os
import platform
import winreg
from pathlib import Path

import qtawesome
import vdf

from PySide6.QtGui import Qt
from PySide6.QtWidgets import QVBoxLayout, QLabel, QGroupBox, QHBoxLayout, QSizePolicy, QPushButton, QFrame, \
    QMessageBox, QFileDialog

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
        self._build_ui()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setContentsMargins(50, 0, 50, 0)

        self.path_label = QLabel()

        path_label_box = QGroupBox()
        path_label_box.setTitle(_("Selected Path"))
        path_label_box.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)
        path_label_box.setLayout(QHBoxLayout())
        path_label_box.layout().addWidget(self.path_label)

        self.status_label = QLabel()
        self.status_label.setObjectName("status_label")
        self.status_label.setText(_("No executable selected"))
        self.status_label.setStyleSheet("color: #6a7282; font-weight: bold;")

        self.select_button = QPushButton(_("Select"))
        self.select_button.clicked.connect(self._handle_select)
        self.select_button.setIcon(qtawesome.icon("fa6s.folder-open"))
        self.select_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        self.search_button = QPushButton(_("Auto find"))
        self.search_button.clicked.connect(self._find_and_validate)
        self.search_button.setIcon(qtawesome.icon("fa6s.magnifying-glass"))
        self.search_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        controls_frame = QFrame()
        controls_frame.setLayout(QHBoxLayout(controls_frame))
        controls_frame.layout().setContentsMargins(0, 0, 0, 0)
        controls_frame.layout().addWidget(self.status_label)
        controls_frame.layout().addWidget(self.search_button)
        controls_frame.layout().addWidget(self.select_button)

        main_layout.addWidget(path_label_box)
        main_layout.addWidget(controls_frame)

        self.exe_not_found_message = QMessageBox(parent=self.controller)
        self.exe_not_found_message.setWindowTitle(_("Until Then executable not found"))
        self.exe_not_found_message.setText(_("We couldn’t locate 'UntilThen.exe' automatically\nPlease choose the game’s executable manually."))
        self.exe_not_found_message.setIcon(QMessageBox.Icon.Warning)
        self.exe_not_found_message.setStandardButtons(QMessageBox.StandardButton.Ok)

    def _find_and_validate(self):
        self._find_until_then_path()
        self._validate_path()

    def showEvent(self, event):
        super().showEvent(event)

        self.controller.next_button.setEnabled(False)

    def _handle_select(self):
        selected_path_dialog = QFileDialog(parent=self.controller)
        selected_path_dialog.setWindowTitle(_("Select UntilThen.exe"))
        selected_path_dialog.setNameFilter("UntilThen.exe")
        selected_path_dialog.exec()

        selected_path = selected_path_dialog.selectedFiles()[0]

        if selected_path:
            self.path_label.setText(selected_path)
            self.controller.state.game_path = Path(selected_path).parent
        self._validate_path()

    def _validate_path(self):
        game_path = self.controller.state.game_path
        exe_path = game_path / GAME_EXE_NAME if game_path else None

        if not exe_path or not exe_path.is_file():
            self.controller.logger.warning(f"{LOG_PREFIX} Valid Until Then executable not found")
            self.status_label.setText(_("UntilThen.exe not found"))
            self.status_label.setStyleSheet("color: #fb2c36")
            self.controller.next_button.setEnabled(False)
            self.search_button.setEnabled(True)
            self.exe_not_found_message.exec()
        else:
            self.controller.logger.info(f"{LOG_PREFIX} Valid Until Then executable found at {exe_path}")
            self.path_label.setText(str(exe_path))
            self.status_label.setText(_("UntilThen.exe found"))
            self.status_label.setStyleSheet("color: #00c951")
            self.controller.next_button.setEnabled(True)
            self.search_button.setEnabled(False)

    def _find_until_then_path(self):
        if self.controller.state.game_path is not None:
            return

        for game_id in [FULL_GAME_ID, DEMO_GAME_ID]:
            path = self._find_game_path_by_id(game_id)
            if path is not None:
                self.controller.logger.info(f"{LOG_PREFIX} The {"full" if game_id==FULL_GAME_ID else "demo" } version of Until Then was found")
                self.controller.state.game_path = path
                self.controller.state.is_demo = (game_id == DEMO_GAME_ID)
                return

        self.controller.logger.info(f"{LOG_PREFIX} No game installation found")
        self.controller.state.game_path = None

    def _find_game_path_by_id(self, game_id: int):
        self.controller.logger.debug(f"{LOG_PREFIX} Trying to auto-detect game path for ID {game_id}")

        steam_path = self._find_steam_path()
        if not steam_path:
            return None

        library_folders_path = steam_path / "steamapps" / "libraryfolders.vdf"
        try:
            with open(library_folders_path, encoding="utf-8") as file:
                library_data = vdf.load(file)
        except FileNotFoundError:
            self.controller.logger.warning(f"{LOG_PREFIX} libraryfolders.vdf not found")
            return None

        libraries = []
        folders = library_data.get("libraryfolders", {})
        for entry in folders.values():
            if isinstance(entry, dict) and "path" in entry:
                libraries.append(Path(entry["path"]))
            elif isinstance(entry, dict):
                libraries.append(Path(str(entry)))

        if not libraries:
            libraries.append(steam_path)

        for library_path in libraries:
            manifest_path = library_path / "steamapps" / f"appmanifest_{game_id}.acf"
            if manifest_path.exists():
                try:
                    with open(manifest_path, encoding="utf-8") as file:
                        manifest = vdf.load(file)
                    install_dir = manifest["AppState"]["installdir"]
                    game_path = library_path / "steamapps" / "common"/ install_dir
                    if game_path.exists():
                        self.controller.logger.debug(f"{LOG_PREFIX} Found game at {game_path}")
                        return game_path.resolve()
                except Exception as error:
                    self.controller.logger.warning(f"{LOG_PREFIX} Failed to parse manifest: {error}")

        self.controller.logger.warning(f"{LOG_PREFIX} Could not auto-detect path for game ID {game_id}")
        return None

    def _find_steam_path(self):
        self.controller.logger.debug(f"{LOG_PREFIX} Trying to find steam path")

        system = platform.system()
        possible_paths = []

        match system:
            case "Windows":
                try:
                    steam_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam")
                    steam_path = winreg.QueryValueEx(steam_key, "SteamPath")
                    winreg.CloseKey(steam_key)
                except FileNotFoundError:
                    self.controller.logger.warning(f"{LOG_PREFIX} Steam path not found in winreg")
                    steam_path = None

                if steam_path:
                    possible_paths.append(Path(steam_path[0]))

                possible_paths = [
                    Path(os.environ.get("ProgramFiles(x86)")) / "Steam",
                    Path(os.environ.get("ProgramFiles", "")) / "Steam",
                ]
            case "Linux":
                possible_paths = [
                    Path().home() / ".steam" / "steam",
                    Path().home() / ".local" / "share" / "Steam",
                    Path().home() / ".var" / "app" / "com.valvesoftware.Steam" / "data" / "Steam",
                ]
            case _:
                self.controller.logger.warning(f"{LOG_PREFIX} Unsupported system: {system}")
                return None

        for path in possible_paths:
            if path.resolve().exists():
                self.controller.logger.debug(f"{LOG_PREFIX} Steam path found at {path}")
                return path.resolve()

        self.controller.logger.info(f"{LOG_PREFIX} Steam not found in standard directories")
        return None