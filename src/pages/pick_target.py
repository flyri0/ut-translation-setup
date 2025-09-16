import os
import platform
from pathlib import Path

import qtawesome
import vdf
from PySide6.QtCore import Signal, Qt, QDir
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGroupBox, \
    QSizePolicy, QHBoxLayout, QPushButton, QFrame, QFileDialog, QMessageBox


class PickTargetPage(QWidget):
    FULL_GAME_ID = 1574820  # full game steam id
    DEMO_GAME_ID = 2296400  # demo steam id

    finished = Signal(Path, bool)

    def __init__(self):
        super().__init__()
        self._ui()
        self.target_path: Path
        self.is_demo: bool

    def _ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.path_label = QLabel()

        path_label_box = QGroupBox()
        path_label_box.setTitle(self.tr("Selected file:"))
        path_label_box.setSizePolicy(
            QSizePolicy.Policy.MinimumExpanding,
            QSizePolicy.Policy.Fixed,
        )
        path_label_box.setLayout(QHBoxLayout())
        path_label_box.layout().addWidget(self.path_label)

        self.status_label = QLabel()
        self.status_label.setText(self.tr("UntilThen.pck not selected"))
        self.status_label.setStyleSheet("color: #6a7282; font-weight: bold;")

        self.pick_file_button = QPushButton(self.tr("Manually Pick"))
        self.pick_file_button.clicked.connect(self._handle_file_pick)
        self.pick_file_button.setIcon(qtawesome.icon("fa6s.folder-open"))
        self.pick_file_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.pick_file_button.setToolTip(self.tr(
            "Manually pick UntilThen.pck from the game installation directory."
        ))

        self.quick_find_button = QPushButton(self.tr("Quick Find"))
        self.quick_find_button.clicked.connect(self._handle_quick_find)
        self.quick_find_button.setIcon(qtawesome.icon("fa6s.magnifying-glass"))
        self.quick_find_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.quick_find_button.setToolTip(self.tr(
            "Automatically searches for UntilThen.pck in common locations;"
            " works only with Steam installs."
        ))

        buttons_frame = QFrame()
        buttons_frame_layout = QHBoxLayout(buttons_frame)
        buttons_frame_layout.setContentsMargins(0, 0, 0, 0)
        buttons_frame_layout.addWidget(self.quick_find_button, 2)
        buttons_frame_layout.addWidget(self.pick_file_button, 1)

        self.next_page_button = QPushButton(self.tr("Next") + " ")
        self.next_page_button.clicked.connect(self._handle_next_page)
        self.next_page_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.next_page_button.setEnabled(False)
        self.next_page_button.setLayoutDirection(
            Qt.LayoutDirection.RightToLeft
        )
        self.next_page_button.setIcon(qtawesome.icon("fa6s.arrow-right"))
        self.next_page_button.setMinimumHeight(50)
        self.next_page_button.setStyleSheet(
            """
            font-size: 15px;
            font-weight: bold;
            """
        )

        layout.addWidget(path_label_box)
        layout.addWidget(buttons_frame)
        layout.addWidget(self.status_label)
        layout.addWidget(self.next_page_button)

        self.pick_file_dialog = QFileDialog(parent=self)
        self.pick_file_dialog.setWindowTitle(self.tr("Pick UntilThen.pck"))
        self.pick_file_dialog.setFilter(QDir.Filter.Files)
        self.pick_file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        self.pick_file_dialog.setNameFilter("UntilThen.pck (*.pck)")

        self.file_not_found_message = QMessageBox(parent=self)
        self.file_not_found_message.setWindowTitle(self.tr("File Not Found"))
        self.file_not_found_message.setText(self.tr(
            "UntilThen.pck could not be located automatically."
            " Please select the game executable manually."
        ))
        self.file_not_found_message.setIcon(QMessageBox.Icon.Warning)
        self.file_not_found_message.setStandardButtons(
            QMessageBox.StandardButton.Ok
        )

        self.file_not_selected_message = QMessageBox(parent=self)
        self.file_not_selected_message.setWindowTitle(self.tr(
            "No file selected"
        ))
        self.file_not_selected_message.setText(self.tr(
            "You did not select UntilThen.pck. Please try again."
        ))
        self.file_not_selected_message.setIcon(QMessageBox.Icon.Information)
        self.file_not_selected_message.setStandardButtons(
            QMessageBox.StandardButton.Ok
        )

    def _handle_file_pick(self):
        self.pick_file_dialog.exec()

        selected_files = self.pick_file_dialog.selectedFiles()
        selected_file = selected_files[0] if selected_files else None

        if selected_file:
            self._validate_file(Path(selected_file))
            return None

        self.file_not_selected_message.exec()
        return None

    def _handle_next_page(self):
        self.finished.emit(self.target_path, self.is_demo)

    def _handle_quick_find(self):
        path = self._find_util_then_pck_path()
        if not path:
            self.file_not_found_message.open()

        self._validate_file(path)

    def _validate_file(self, path: Path | None):

        if not path:
            self._set_status(is_valid=False)
            return None

        is_demo = True if path.parent.name == "Until Then Demo" else False
        if path.exists() and path.is_file() and path.suffix == ".pck":
            self._set_status(is_valid=True, is_demo=is_demo)
            self.target_path = path
            self.is_demo = is_demo
            self.path_label.setText(str(path))
            self.pick_file_button.setEnabled(False)
            self.quick_find_button.setEnabled(False)
            self.next_page_button.setEnabled(True)
            self.next_page_button.setDefault(True)
            return None

        self._set_status(is_valid=False)
        return None

    def _find_util_then_pck_path(self):
        for game_id in [self.FULL_GAME_ID, self.DEMO_GAME_ID]:
            install_dir = self._find_game_path_by_id(game_id)
            if install_dir is None:
                continue

            candidate = install_dir / "UntilThen.pck"
            if candidate.is_file():
                abs_file_path = candidate.resolve()
                return abs_file_path

        return None

    def _set_status(self, is_valid: bool, is_demo: bool = False):
        if is_valid:
            if is_demo:
                demo_message = self.tr(
                    ". You're using the demo version of Until Then"
                )
            else:
                demo_message = ""

            self.status_label.setText(self.tr(
                "UntilThen.pck is valid"
            ) + demo_message)
            self.status_label.setStyleSheet(
                "color: #00c951; font-weight: bold;"
            )
        else:
            self.status_label.setText(self.tr(
                "A valid file could not be found."
            ))
            self.status_label.setStyleSheet(
                "color: #fb2c36; font-weight: bold;"
            )

    def _find_game_path_by_id(self, game_id: int):
        steam_path = self._find_steam_path()
        if not steam_path:
            return None

        library_folders_path = steam_path / "steamapps" / "libraryfolders.vdf"
        try:
            with open(library_folders_path, encoding="utf-8") as file:
                library_data = vdf.load(file)
        except FileNotFoundError:
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
                with open(manifest_path, encoding="utf-8") as file:
                    manifest = vdf.load(file)
                install_dir = manifest["AppState"]["installdir"]
                game_path = (library_path
                             / "steamapps"
                             / "common"
                             / install_dir
                             )
                if game_path.exists():
                    return Path(game_path.resolve())

        return None

    @staticmethod
    def _find_steam_path():

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
                return None

        for path in possible_paths:
            if path.resolve().exists():
                return path

        return None
