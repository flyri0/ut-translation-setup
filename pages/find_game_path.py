import gettext
import os
import platform
from pathlib import Path

import qtawesome
import vdf
from PySide6.QtCore import QDir

from PySide6.QtGui import Qt
from PySide6.QtWidgets import QVBoxLayout, QLabel, QGroupBox, QHBoxLayout, QSizePolicy, QPushButton, QFrame, \
    QMessageBox, QFileDialog

from pages.base import BasePage

_ = gettext.gettext

FULL_GAME_ID = 1574820
DEMO_GAME_ID = 2296400
LOG_PREFIX = "FindGamePath:"

class FindGamePath(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.controller.logger.debug(f"{LOG_PREFIX} Initialized page")
        self._build_ui()
        self.controller.logger.debug(f"{LOG_PREFIX} UI built")

    def _build_ui(self):
        self.controller.logger.debug(f"{LOG_PREFIX} Building UI elements")
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.path_label = QLabel()

        path_label_box = QGroupBox()
        path_label_box.setTitle(_("Local Selecionado"))
        path_label_box.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)
        path_label_box.setLayout(QHBoxLayout())
        path_label_box.layout().addWidget(self.path_label)

        self.status_label = QLabel()
        self.status_label.setObjectName("status_label")
        self.status_label.setText(_("Nenhum executável selecionado"))
        self.status_label.setStyleSheet("color: #6a7282; font-weight: bold;")

        self.select_button = QPushButton(_("Selecionar"))
        self.select_button.clicked.connect(self._handle_select)
        self.select_button.setIcon(qtawesome.icon("fa6s.folder-open"))

        self.search_button = QPushButton(_("Busca Rápida"))
        self.search_button.clicked.connect(self._find_and_validate)
        self.search_button.setIcon(qtawesome.icon("fa6s.magnifying-glass"))
        self.search_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        controls_frame = QFrame()
        controls_frame.setLayout(QHBoxLayout(controls_frame))
        controls_frame.layout().setContentsMargins(0, 0, 0, 0)
        controls_frame.layout().addWidget(self.search_button)
        controls_frame.layout().addWidget(self.select_button)

        main_layout.addWidget(path_label_box)
        main_layout.addWidget(controls_frame)
        main_layout.addWidget(self.status_label)

        self.select_path_dialog = QFileDialog(parent=self.controller)
        self.select_path_dialog.setWindowTitle(_("Selecionar Executável"))
        self.select_path_dialog.setFilter(QDir.Filter.Files)
        self.select_path_dialog.setNameFilter("UntilThen.exe UntilThen.x86_64")
        self.select_path_dialog.setDirectory(str(Path.home().absolute().resolve()))

        self.exe_not_found_message = QMessageBox(parent=self.controller)
        self.exe_not_found_message.setWindowTitle(_("Executável não encontrado"))
        self.exe_not_found_message.setText(_(
            "Não foi possível localizar o arquivo “UntilThen.exe” automaticamente"
            "\nPor favor, selecione o executável do jogo manualmente."
        ))
        self.exe_not_found_message.setIcon(QMessageBox.Icon.Warning)
        self.exe_not_found_message.setStandardButtons(QMessageBox.StandardButton.Ok)

        self.file_not_selected_message = QMessageBox(parent=self.controller)
        self.file_not_selected_message.setWindowTitle(_("Nenhum arquivo selecionado"))
        self.file_not_selected_message.setText(_(
            "Você não selecionou um executável válido\nPor favor, tente novamente."
        ))
        self.file_not_selected_message.setIcon(QMessageBox.Icon.Information)
        self.file_not_selected_message.setStandardButtons(QMessageBox.StandardButton.Ok)
        self.controller.logger.debug(f"{LOG_PREFIX} Dialogs initialized")

    def _find_and_validate(self):
        self.controller.logger.debug(f"{LOG_PREFIX} Starting auto-find and validate sequence")
        self._find_until_then_path()
        self._validate_path()

    def showEvent(self, event):
        super().showEvent(event)
        self.controller.logger.debug(f"{LOG_PREFIX} showEvent: disabling next until valid")
        self.controller.next_button.setEnabled(False)
        self.controller.back_button.setEnabled(True)

    def _handle_select(self):
        self.controller.logger.debug(f"{LOG_PREFIX} Opening file dialog for manual selection")
        self.select_path_dialog.exec()

        selected_files = self.select_path_dialog.selectedFiles()
        selected_path = selected_files[0] if selected_files else None
        self.controller.logger.debug(f"{LOG_PREFIX} User selected: {selected_path}")

        if selected_path:
            self.path_label.setText(selected_path)
            self.controller.state.game_path = Path(selected_path)
            self.controller.logger.info(f"{LOG_PREFIX} Manual path set to {self.controller.state.game_path}")
            self._validate_path()
            return

        self.controller.logger.info(f"{LOG_PREFIX} No file selected by user")
        self.file_not_selected_message.exec()

    def _validate_path(self):
        game_path = self.controller.state.game_path

        if not game_path:
            self.controller.logger.warning(f"{LOG_PREFIX} No game path set")
            self._report_missing_pck()
            return

        pck_path = Path(game_path).parent / "UntilThen.pck"
        self.controller.logger.debug(f"{LOG_PREFIX} Validating PCK file at: {pck_path}")

        if not pck_path.is_file():
            self.controller.logger.warning(f"{LOG_PREFIX} UntilThen.pck not found at {pck_path}")
            self._report_missing_pck()
            return
        else:
            self.controller.logger.info(f"{LOG_PREFIX} UntilThen.pck found at {pck_path}")
            self._report_pck_found(game_path)

    def _report_missing_pck(self):
        self.status_label.setText(_("UntilThen.pck não encontrado"))
        self.status_label.setStyleSheet("color: #fb2c36")
        self.controller.next_button.setEnabled(False)
        self.search_button.setEnabled(True)
        self.exe_not_found_message.exec()

    def _report_pck_found(self, game_path: Path):
        self.path_label.setText(str(game_path.resolve()))
        self.status_label.setText(_("UntilThen.pck encontrado"))
        self.status_label.setStyleSheet("color: #00c951")
        self.controller.next_button.setEnabled(True)
        self.search_button.setEnabled(False)
        self.select_button.setEnabled(False)

    def _find_until_then_path(self):
        self.controller.logger.debug(f"{LOG_PREFIX} Auto-detect path sequence started")

        exe_names = ("UntilThen.exe", "UntilThen.x86_64")

        for game_id in (FULL_GAME_ID, DEMO_GAME_ID):
            install_dir = self._find_game_path_by_id(game_id)
            if install_dir is None:
                continue

            install_dir = Path(install_dir)
            for exe_name in exe_names:
                candidate = Path(install_dir / exe_name)
                if candidate.is_file():
                    ver = "full" if game_id == FULL_GAME_ID else "demo"
                    abs_exe = candidate.resolve()
                    self.controller.logger.info(
                        f"{LOG_PREFIX} The {ver} version of UntilThen was found at {abs_exe}"
                    )
                    self.controller.state.game_path = abs_exe
                    self.controller.state.is_demo = (game_id == DEMO_GAME_ID)
                    return

            self.controller.logger.info(f"{LOG_PREFIX} No game installation found after detection attempts")
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
            self.controller.logger.warning(f"{LOG_PREFIX} libraryfolders.vdf not found at {library_folders_path}")
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
                    game_path = library_path / "steamapps" / "common" / install_dir
                    if game_path.exists():
                        self.controller.logger.debug(f"{LOG_PREFIX} Found game directory at {game_path}")
                        return game_path.resolve()
                except Exception as error:
                    self.controller.logger.warning(f"{LOG_PREFIX} Failed to parse manifest: {error}")

        self.controller.logger.warning(f"{LOG_PREFIX} Could not auto-detect path for game ID {game_id}")
        return None

    def _find_steam_path(self):
        self.controller.logger.debug(f"{LOG_PREFIX} Trying to find steam installation path")

        system = platform.system()
        possible_paths = []

        match system:
            case "Windows":
                import winreg

                try:
                    steam_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam")
                    steam_path = winreg.QueryValueEx(steam_key, "SteamPath")
                    winreg.CloseKey(steam_key)
                except FileNotFoundError:
                    self.controller.logger.warning(f"{LOG_PREFIX} Steam path not found in registry")
                    steam_path = None

                if steam_path:
                    possible_paths.append(Path(steam_path[0]))
                possible_paths.extend([
                    Path(os.environ.get("ProgramFiles(x86)", "")) / "Steam",
                    Path(os.environ.get("ProgramFiles", "")) / "Steam",
                ])
            case "Linux":
                possible_paths = [
                    Path().home() / ".steam" / "steam",
                    Path().home() / ".local" / "share" / "Steam",
                    Path().home() / ".local" / "share" / "Steam",
                    Path().home() / "snap" / "steam" / "common" / ".local" / "share" / "Steam",
                    Path().home() / ".var" / "app" / "com.valvesoftware.Steam" / "data" / "Steam",

                ]
            case _:
                self.controller.logger.warning(f"{LOG_PREFIX} Unsupported system: {system}")
                return None

        for path in possible_paths:
            if path.resolve().exists():
                self.controller.logger.debug(f"{LOG_PREFIX} Steam path found at {path}")
                return path.resolve()

        self.controller.logger.info(f"{LOG_PREFIX} Steam not found in standard directories: {possible_paths}")
        return None