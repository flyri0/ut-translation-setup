import gettext

import qtawesome
from PySide6.QtCore import QSize, Qt, QObject, QEvent
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QStackedWidget, QFrame,
    QPushButton, QHBoxLayout, QMessageBox, QLabel, QSizePolicy
)
from screeninfo import get_monitors

from logger import _Logger
from pages.unzip_files import UnzipFilesPage
from pages.find_game_path import FindGamePath
from pages.verify_version import VerifyVersionPage
from pages.welcome import WelcomePage
from state import AppState

import assets  # type: ignore

_ = gettext.gettext
LOG_PREFIX = "App:"


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.state = AppState()
        self.logger = _Logger.get_logger()
        self.logger.info(f"{LOG_PREFIX} Application initialized")

        self.page_sequence = [VerifyVersionPage, WelcomePage, FindGamePath, UnzipFilesPage]
        self.current_index = 0

        self.logger.debug(f"{LOG_PREFIX} Building UI")
        self._build_ui()
        self.logger.debug(f"{LOG_PREFIX} Centering window")
        self.setWindowIcon(QIcon(":/assets/icon.ico"))
        self.setWindowTitle(_("Until Then - Instalar Tradução"))
        self._center_window()

        self.logger.debug(f"{LOG_PREFIX} Showing initial page")
        self._show_page(0)

    def _build_ui(self):
        self.logger.debug(f"{LOG_PREFIX} Setting up central widget and layouts")
        central = QWidget()
        central.setStyleSheet("QPushButton { padding: 10px; }")
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.stack = QStackedWidget()
        page_layout = QHBoxLayout()
        page_layout.setContentsMargins(0, 0, 0, 0)

        self.banner = ScaledLabel()
        self.banner.setPixmap(QPixmap(":/assets/banner.png"))
        self.banner.setAlignment(Qt.AlignmentFlag.AlignLeft)

        page_layout.addWidget(self.banner)
        page_layout.addWidget(self.stack, stretch=1)

        page_frame = QFrame()
        page_frame.setLayout(page_layout)

        self.logger.debug(f"{LOG_PREFIX} Instantiating pages")
        for page_cls in self.page_sequence:
            page = page_cls(parent=self, controller=self)
            self.stack.addWidget(page)

        self.line = QFrame()
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.logger.debug(f"{LOG_PREFIX} Creating navigation buttons")
        button_layout = QHBoxLayout()
        self.cancel_button = QPushButton(qtawesome.icon("fa6s.xmark"), _("Cancelar"))
        self.back_button = QPushButton(qtawesome.icon("fa6s.chevron-left"), _("Voltar"))
        self.next_button = QPushButton(qtawesome.icon("fa6s.chevron-right"), _("Próximo"))

        self.cancel_button.clicked.connect(self.close)
        self.back_button.clicked.connect(self.previous_page)
        self.next_button.clicked.connect(self.next_page)

        button_layout.addWidget(self.cancel_button)
        button_layout.addStretch(1)
        button_layout.addWidget(self.back_button)
        button_layout.addWidget(self.next_button)

        self.button_container = QWidget()
        self.button_container.setLayout(button_layout)

        main_layout.addWidget(page_frame)
        main_layout.addWidget(self.line)
        main_layout.addWidget(self.button_container)
        self.logger.debug(f"{LOG_PREFIX} UI build complete")

    def _show_page(self, index: int):
        self.logger.debug(f"{LOG_PREFIX} Switching to page index {index}")
        if not (0 <= index < self.stack.count()):
            self.logger.warning(f"{LOG_PREFIX} Page index {index} out of bounds")
            return
        self.stack.setCurrentIndex(index)
        self.current_index = index
        widget = self.stack.currentWidget()
        self.logger.info(f"{LOG_PREFIX} Displayed page: {type(widget).__name__}")

    def next_page(self):
        self.logger.debug(f"{LOG_PREFIX} Next page requested from index {self.current_index}")
        self._show_page(self.current_index + 1)

    def previous_page(self):
        self.logger.debug(f"{LOG_PREFIX} Previous page requested from index {self.current_index}")
        self._show_page(self.current_index - 1)

    def _center_window(self):
        self.logger.debug(f"{LOG_PREFIX} Centering and sizing the window")
        for monitor in get_monitors():
            if monitor.is_primary:
                screen_width, screen_height = monitor.width, monitor.height
                break
        else:
            screen_width, screen_height = 1280, 720

        max_width = screen_width * 0.5
        max_height = screen_height * 0.5
        target_ratio = 4 / 3

        width = max_width
        height = width / target_ratio
        if height > max_height:
            height = max_height
            width = height * target_ratio

        self.setFixedSize(int(width), int(height))
        geom = self.frameGeometry()
        center = self.screen().availableGeometry().center()
        geom.moveCenter(center)
        self.move(geom.topLeft())
        self.logger.debug(f"{LOG_PREFIX} Window centered at ({width}x{height})")

    def closeEvent(self, event):
        self.logger.info(f"{LOG_PREFIX} Close event triggered")
        message_box = QMessageBox(parent=self)
        message_box.setWindowTitle(_("Exit?"))
        message_box.setText(_("Are you sure you want to exit?"))
        message_box.setIcon(QMessageBox.Icon.Question)
        message_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        message_box.setDefaultButton(QMessageBox.StandardButton.No)

        result = message_box.exec()
        self.logger.debug(f"{LOG_PREFIX} Close dialog result: {result}")

        match result:
            case QMessageBox.StandardButton.Yes:
                self.logger.info(f"{LOG_PREFIX} User confirmed exit")
                event.accept()
            case QMessageBox.StandardButton.No:
                self.logger.info(f"{LOG_PREFIX} User canceled exit")
                event.ignore()

class ScaledLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._pixmap = None
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

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
