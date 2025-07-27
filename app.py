import gettext

import qtawesome
from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon, QPixmap, Qt
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QStackedWidget, QFrame, QPushButton, \
    QHBoxLayout, QMessageBox, QLabel, QSizePolicy
from screeninfo import get_monitors

from logger import _Logger
from pages.unzip_files import UnzipFilesPage
from pages.select_game_path import SelectGamePathPage
from pages.welcome import WelcomePage
from state import AppState

import assets # type: ignore

_ = gettext.gettext
LOG_PREFIX = "App:"

class App(QMainWindow):
    def __init__(self):
        super().__init__()

        self.state = AppState()
        self.logger = _Logger.get_logger()
        self.logger.info(f"{LOG_PREFIX} Initialized")

        self.page_sequence = [WelcomePage, SelectGamePathPage, UnzipFilesPage]
        self.current_index: int = 0

        self._build_ui()
        self.setWindowIcon(QIcon(":/assets/icon.ico"))
        self.setWindowTitle(_("Until Then - Instalar Tradução"))
        self._center_window()
        self._show_page(0)

    def _build_ui(self):
        central = QWidget()
        central.setStyleSheet("QPushButton { padding: 10px; }")
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.stack = QStackedWidget()

        page_layout = QHBoxLayout()
        page_layout.setContentsMargins(0, 0, 0, 0)

        banner = ScaledLabel()
        banner.setPixmap(QPixmap(":/assets/banner.png"))
        banner.setAlignment(Qt.AlignmentFlag.AlignLeft)

        page_layout.addWidget(banner)
        page_layout.addWidget(self.stack, stretch=1)

        page_frame = QFrame()
        page_frame.setLayout(page_layout)

        for page_cls in self.page_sequence:
            page = page_cls(parent=self, controller=self)
            self.stack.addWidget(page)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)

        button_layout = QHBoxLayout()

        self.cancel_button = QPushButton(qtawesome.icon("fa6s.xmark"), _("Cancelar"))
        self.back_button = QPushButton(qtawesome.icon("fa6s.chevron-left"), _("Voltar"))
        self.next_button = QPushButton(qtawesome.icon("fa6s.chevron-right"), _("Próximo"))

        self.cancel_button.clicked.connect(self.close)
        self.back_button.clicked.connect(self._previous_page)
        self.next_button.clicked.connect(self._next_page)

        button_layout.addWidget(self.cancel_button)
        button_layout.addStretch(1)
        button_layout.addWidget(self.back_button)
        button_layout.addWidget(self.next_button)

        button_container = QWidget()
        button_container.setLayout(button_layout)

        main_layout.addWidget(page_frame)
        main_layout.addWidget(line)
        main_layout.addWidget(button_container)

    def _show_page(self, index: int):
        if not (0 <= index < self.stack.count()):
            self.logger.warning(f"{LOG_PREFIX} Page index {index} out of bounds")
            return

        self.stack.setCurrentIndex(index)
        self.current_index = index
        self.logger.info(f"{LOG_PREFIX} Page {type(self.stack.currentWidget()).__name__} displayed")

    def _next_page(self):
        self._show_page(self.current_index + 1)

    def _previous_page(self):
        self._show_page(self.current_index - 1)

    def _center_window(self):
        for monitor in get_monitors():
            if monitor.is_primary:
                screen_width, screen_height = monitor.width, monitor.height
                break
        else:
            screen_width, screen_height = 1280, 720

        target_aspect_width, target_aspect_height = 4, 3 # target aspect ratio (width x height)
        max_width_ratio, max_height_ratio = 0.5, 0.5 # maximum fraction of the screen the window may occupy in %

        max_window_width = screen_width * max_width_ratio
        max_window_height = screen_height * max_height_ratio

        window_width = max_window_width
        window_height = (window_width * target_aspect_height) / target_aspect_width

        if window_height > max_window_height:
            window_height = max_window_height
            window_width = (window_height * target_aspect_width) / target_aspect_height

        self.setFixedSize(int(window_width), int(window_height))
        frame_geometry = self.frameGeometry()
        screen_center = self.screen().availableGeometry().center()
        frame_geometry.moveCenter(screen_center)
        self.move(frame_geometry.topLeft())

    def closeEvent(self, event):
        self.logger.info(f"{LOG_PREFIX} Termination requested by user")
        message_box = QMessageBox(parent=self)
        message_box.setWindowTitle("Exit?")
        message_box.setText("Are you sure you want to exit?")
        message_box.setIcon(QMessageBox.Icon.Question)
        message_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        message_box.setDefaultButton(QMessageBox.StandardButton.No)

        result = message_box.exec()

        match result:
            case QMessageBox.StandardButton.Yes:
                event.accept()
            case QMessageBox.StandardButton.No:
                self.logger.info(f"{LOG_PREFIX} Termination aborted by user")
                event.ignore()

class ScaledLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._pixmap = None
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )

    def setPixmap(self, pixmap: QPixmap):
        self._pixmap = pixmap
        super().setPixmap(pixmap)

    def resizeEvent(self, event):
        if self._pixmap:
            scaled = self._pixmap.scaled(
                QSize(int(self._pixmap.width() * self.height() / self._pixmap.height()), self.height()),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            super().setPixmap(scaled)
        super().resizeEvent(event)