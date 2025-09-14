import qtawesome
from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGroupBox, \
    QSizePolicy, QHBoxLayout, QPushButton


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

        path_label_box = QGroupBox(self)
        path_label_box.setTitle(self.tr("Selected file:"))
        path_label_box.setSizePolicy(
            QSizePolicy.Policy.MinimumExpanding,
            QSizePolicy.Policy.Fixed,
        )
        path_label_box.setLayout(QHBoxLayout())
        path_label_box.layout().addWidget(path_label_box)

        self.status_label = QLabel()
        self.status_label.setText(self.tr("UntilThen.pck not selected"))
        self.status_label.setStyleSheet("color: #6a7282; font-weight: bold;")

        self.pick_file_button = QPushButton(self.tr("Pick UntilThen.pck"))
        # self.pick_file_button.clicked.connect(self._handle_file_pick)
        self.pick_file_button.setIcon(qtawesome.icon("fa6s.folder-open"))

        self.quick_find_button = QPushButton(self.tr("Quick Find"))
        # self.quick_find_button.clicked.connect(self._handle_quick_find)
        self.quick_find_button.setIcon(qtawesome.icon("fa6s.magnifying-glass"))

        layout.addWidget(path_label_box)
        layout.addWidget(self.status_label)
