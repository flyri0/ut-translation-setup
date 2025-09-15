import qtawesome
from PySide6.QtCore import Signal, Qt, QDir
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGroupBox, \
    QSizePolicy, QHBoxLayout, QPushButton, QFrame, QFileDialog, QMessageBox


class PickTargetPage(QWidget):
    FULL_GAME_ID = 1574820  # full game steam id
    DEMO_GAME_ID = 2296400  # demo steam id

    finished = Signal()

    def __init__(self):
        super().__init__()
        self._ui()

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
        # self.quick_find_button.clicked.connect(self._handle_quick_find)
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

        layout.addWidget(path_label_box)
        layout.addWidget(buttons_frame)
        layout.addWidget(self.status_label)

        self.pick_file_dialog = QFileDialog(parent=self)
        self.pick_file_dialog.setWindowTitle(self.tr("Pick UntilThen.pck"))
        self.pick_file_dialog.setFilter(QDir.Filter.Files)
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
            self.path_label.setText(selected_file)

        self.file_not_selected_message.exec()
