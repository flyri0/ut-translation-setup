import os
import platform
from pathlib import Path

import qtawesome
import vdf
from PySide6.QtCore import QDir
from PySide6.QtGui import Qt
from PySide6.QtWidgets import QVBoxLayout, QLabel, QGroupBox, QSizePolicy, \
    QHBoxLayout, QPushButton, QFrame, QFileDialog, QMessageBox

from src.pages.base import BasePage


class FindGamePathPage(BasePage):
    FULL_GAME_ID = 1574820
    DEMO_GAME_ID = 2296400

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.path_label = QLabel()

        path_label_box = QGroupBox()
        path_label_box.setTitle(self.tr("Selected Path"))
        path_label_box.setSizePolicy(
            QSizePolicy.Policy.MinimumExpanding,
            QSizePolicy.Policy.Fixed
        )
        path_label_box.setLayout(QHBoxLayout())
        path_label_box.layout().addWidget(self.path_label)

        self.status_label = QLabel()
        self.status_label.setText(self.tr("UntilThen.pck not selected"))
        self.status_label.setStyleSheet("color: #6a7282; font-weight: bold;")

        self.pick_file_button = QPushButton(self.tr("Select UntilThen.pck"))
        self.pick_file_button.clicked.connect(self._handle_file_selection)
        self.pick_file_button.setIcon(qtawesome.icon("fa6s.folder-open"))
        self.pick_file_button.setSizePolicy(
            QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.Fixed
        )

        self.quick_find_button = QPushButton(self.tr("Quick Find"))
        self.quick_find_button.clicked.connect(self._handle_quick_find)
        self.quick_find_button.setIcon(qtawesome.icon("fa6s.magnifying-glass"))

        buttons_frame = QFrame()
        buttons_frame.setLayout(QHBoxLayout(buttons_frame))
        buttons_frame.layout().setContentsMargins(0, 0, 0, 0)
        buttons_frame.layout().addWidget(self.quick_find_button)
        buttons_frame.layout().addWidget(self.pick_file_button)

        layout.addWidget(path_label_box)
        layout.addWidget(buttons_frame)
        layout.addWidget(self.status_label)

        self.select_file_dialog = QFileDialog(parent=self.controller)
        self.select_file_dialog.setWindowTitle(self.tr("Select UntilThen.pck"))
        self.select_file_dialog.setFilter(QDir.Filter.Files)
        self.select_file_dialog.setNameFilter("UntilThen.pck (*.pck)")
        self.select_file_dialog.setDirectory(
            str(Path.home().absolute().resolve())
        )

        self.file_not_found_message = QMessageBox(parent=self.controller)
        self.file_not_found_message.setWindowTitle(
            self.tr("Executável não encontrado"))
        self.file_not_found_message.setText(self.tr(
            "The file 'UntilThen.pck' could not be located automatically"
            " Please select the game executable manually."
        ))
        self.file_not_found_message.setIcon(QMessageBox.Icon.Warning)
        self.file_not_found_message.setStandardButtons(
            QMessageBox.StandardButton.Ok)

        self.file_not_selected_message = QMessageBox(parent=self.controller)
        self.file_not_selected_message.setWindowTitle(self.tr(
            "No file selected"
        ))
        self.file_not_selected_message.setText(self.tr(
            "You did not select the UntilThen.pck file. Please try again."
        ))
        self.file_not_selected_message.setIcon(QMessageBox.Icon.Information)
        self.file_not_selected_message.setStandardButtons(
            QMessageBox.StandardButton.Ok
        )

    def showEvent(self, event):
        super().showEvent(event)

        if not self.controller.state.is_valid_file:
            self.controller.next_button.setEnabled(False)

        self.controller.back_button.setEnabled(True)

    def _handle_file_selection(self):
        self.select_file_dialog.exec()

        selected_files = self.select_file_dialog.selectedFiles()
        selected_file = selected_files[0] if selected_files else None
        self.controller.logger.debug("User selected file %s", selected_file)

        if selected_file:
            self.path_label.setText(selected_file)
            self.controller.state.pck_path = Path(selected_file)
            self._validate_file()
            return None

        self.controller.logger.debug("No file selected by user")
        self.file_not_selected_message.exec()
        return None

    def _report_missing_file(self):
        self.status_label.setText(self.tr("UntilThen.pck not found"))
        self.status_label.setStyleSheet("color: #fb2c36")
        self.controller.next_button.setEnabled(False)
        self.quick_find_button.setEnabled(True)
        self.file_not_found_message.exec()

    def _report_file_found(self, path: Path):
        self.path_label.setText(str(path))
        self.status_label.setText(self.tr("UntilThen.pck found"))
        self.status_label.setStyleSheet("color: #00c951")
        self.controller.next_button.setEnabled(True)
        self.quick_find_button.setEnabled(False)
        self.pick_file_button.setEnabled(False)

    def _validate_file(self):
        pck_path = self.controller.state.pck_path

        if not pck_path:
            self.controller.logger.warning(
                "Game path not set, cannot validate file"
            )
            self._report_missing_file()
            return None

        self.controller.logger.debug(
            f"Validating PCK file at {pck_path}"
        )

        if pck_path.is_file():
            self.controller.logger.info(
                f"UntilThen.pck validated"
            )
            self._report_file_found(pck_path)
            self.controller.state.is_valid_file = True
            return None
        else:
            self.controller.logger.warning(
                "Invalid UntilThen.pck"
            )
            self._report_missing_file()
            return None

    def _handle_quick_find(self):
        self._find_util_then_pck_path()
        self._validate_file()

    def _find_util_then_pck_path(self):
        self.controller.logger.debug("Trying to auto-detect game path")

        for game_id in [self.FULL_GAME_ID, self.DEMO_GAME_ID]:
            install_dir = Path(self._find_game_path_by_id(game_id))
            if install_dir is None:
                continue

            candidate = install_dir / "UntilThen.pck"
            if candidate.is_file():
                ver = "full" if game_id == self.FULL_GAME_ID else "demo"
                abs_file_path = candidate.resolve()
                self.controller.logger.debug(
                    "Found UntilThen.pck at"
                    f" {abs_file_path} (game version {ver})"
                )
                self.controller.state.pck_path = abs_file_path
                return None

        self.logger.info("No game installation found")
        self.controller.state.pck_path = None
        return None

    def _find_game_path_by_id(self, game_id: int):
        self.controller.logger.debug(
            f"Trying to auto-detect game path for ID {game_id}"
        )

        steam_path = self._find_steam_path()
        if not steam_path:
            return None

        library_folders_path = steam_path / "steamapps" / "libraryfolders.vdf"
        try:
            with open(library_folders_path, encoding="utf-8") as file:
                library_data = vdf.load(file)
        except FileNotFoundError:
            self.controller.logger.warning(
                f"libraryfolders.vdf not found at {library_folders_path}")
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
            manifest_path = (library_path
                             / "steamapps"
                             / f"appmanifest_{game_id}.acf")
            if manifest_path.exists():
                try:
                    with open(manifest_path, encoding="utf-8") as file:
                        manifest = vdf.load(file)
                    install_dir = manifest["AppState"]["installdir"]
                    game_path = (library_path
                                 / "steamapps"
                                 / "common"
                                 / install_dir
                                 )
                    if game_path.exists():
                        self.controller.logger.debug(
                            f"Found game directory at {game_path}")
                        return game_path.resolve()
                except Exception as error:
                    self.controller.logger.warning(
                        f"Failed to parse manifest: {error}")

        self.controller.logger.warning(
            f"Could not auto-detect path for game ID {game_id}")
        return None

    def _find_steam_path(self):
        self.controller.logger.debug("Trying to find steam installation path")

        system = platform.system()
        possible_paths = []

        match system:
            case "Windows":
                import winreg

                try:
                    steam_key = winreg.OpenKey(
                        winreg.HKEY_CURRENT_USER,
                        r"Software\Valve\Steam"
                    )
                    steam_path = winreg.QueryValueEx(
                        steam_key,
                        "SteamPath"
                    )
                    winreg.CloseKey(steam_key)
                except OSError:
                    self.controller.logger.warning(
                        "Steam path not found in registry"
                    )
                    steam_path = None

                if steam_path:
                    possible_paths.append(Path(steam_path[0]))
                possible_paths.extend([
                    Path(os.environ.get("ProgramFiles(x86)", "")) / "Steam",
                    Path(os.environ.get("ProgramFiles", "")) / "Steam",
                ])

            case "Linux":
                possible_paths = [
                    Path().home()
                    / ".steam"
                    / "steam",
                    Path().home()
                    / ".local"
                    / "share"
                    / "Steam",
                    Path().home()
                    / ".local"
                    / "share"
                    / "Steam",
                    Path().home()
                    / "snap"
                    / "steam"
                    / "common"
                    / ".local"
                    / "share"
                    / "Steam",
                    Path().home()
                    / ".var"
                    / "app"
                    / "com.valvesoftware.Steam"
                    / "data"
                    / "Steam",
                ]
            case _:
                self.controller.logger.warning(f"Unsupported system: {system}")
                return None

        for path in possible_paths:
            if path.resolve().exists():
                self.controller.logger.debug(
                    f"Steam path found at {path}"
                )
                return path

        self.controller.logger.info(
            f"Steam not found in standard directories: {possible_paths}"
        )
        return None
