from pathlib import Path
from typing import Type

import qtawesome
from PySide6.QtCore import QResource, QSize, QUrl
from PySide6.QtGui import QIcon, QPixmap, Qt, QGuiApplication, QDesktopServices
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, \
    QStackedWidget, QHBoxLayout, QSizePolicy, QFrame, QPushButton, \
    QMessageBox, QLabel, QApplication

from src.logger import Logger
from src.pages.base import BasePage
from src.pages.find_game_path import FindGamePathPage
from src.pages.install_files import InstallFilesPage
from src.pages.verify_version import VerifyVersionPage
from src.pages.welcome import WelcomePage


class App(QMainWindow):
    def __init__(self):
        super().__init__()

        self.logger = Logger().get_logger()

        QResource.registerResource('src/resources.rcc')
        self.logger.info("Application Initialized")

        # The sequence of page classes shown in the wizard
        self.page_sequence: list[Type[BasePage]] = [
            VerifyVersionPage,
            WelcomePage,
            FindGamePathPage,
            InstallFilesPage
        ]
        self.current_index = 0

        self.setWindowIcon(QIcon(":icon"))
        self.setWindowTitle(self.tr("Until Then - Install Translation"))
        self._build_ui()

        self._center_window()
        self._show_page(0)

    def _build_ui(self):
        self.logger.debug("Building UI...")
        central = QWidget()
        central.setStyleSheet("QPushButton { padding: 10px; }")
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.stack = QStackedWidget()

        page_layout = QHBoxLayout()
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.setSpacing(0)

        self.banner = ScaledLabel()
        banner_pixmap = QPixmap(":banner")
        if banner_pixmap and not banner_pixmap.isNull():
            self.banner.setPixmap(banner_pixmap)
        else:
            self.logger.warning(
                "Banner pixmap not found or null resource ':banner'"
            )

        self.banner.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )
        self.banner.setSizePolicy(
            QSizePolicy.Policy.MinimumExpanding,
            QSizePolicy.Policy.Expanding
        )

        page_layout.addWidget(self.banner)
        page_layout.addWidget(self.stack, stretch=1)

        page_frame = QFrame()
        page_frame.setLayout(page_layout)

        self.logger.debug("Instantiating pages")
        for page_cls in self.page_sequence:
            try:
                page = page_cls(parent=self, controller=self)
                page.error.connect(self._on_page_error)
                self.stack.addWidget(page)
            except Exception as error:
                self.logger.error(
                    f'Failed to instantiate page "{page_cls.__name__}"'
                )
                raise error

        self.line = QFrame()
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        button_layout = QHBoxLayout()

        self.cancel_button = QPushButton(
            qtawesome.icon("fa6s.xmark"),
            self.tr("Cancel")
        )
        self.back_button = QPushButton(
            qtawesome.icon("fa6s.chevron-left"),
            self.tr("Back")
        )
        self.next_button = QPushButton(
            qtawesome.icon("fa6s.chevron-right"),
            self.tr("Next")
        )

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

    def _show_page(self, index):
        self.logger.debug(f"Switching to page index {index}")
        if not (0 <= index < self.stack.count()):
            self.logger.error(f"Page index {index} is out of bounds")
            return None

        self.stack.setCurrentIndex(index)
        self.current_index = index
        widget = self.stack.currentWidget()
        self.logger.info(f"Displayed page: {type(widget).__name__}")
        return None

    def next_page(self):
        self.logger.debug(
            f"Next page requested from index {self.current_index}"
        )
        self._show_page(self.current_index + 1)

    def previous_page(self):
        self.logger.debug(
            f"Previous page requested from index {self.current_index}"
        )
        self._show_page(self.current_index - 1)

    def _center_window(self):
        self.logger.debug("Centering and sizing the window")

        screen = QGuiApplication.primaryScreen()
        if screen is None:
            screens = QGuiApplication.screens()
            screen = screens[0] if screens else None

        if screen:
            screen_geometry = screen.availableGeometry()
            screen_width = screen_geometry.width()
            screen_height = screen_geometry.height()
        else:
            screen_width, screen_height = 1280, 720
            screen_geometry = None

        max_width = int(screen_width * 0.5)
        max_height = int(screen_height * 0.5)
        target_ratio = 4 / 3

        width = max_width
        height = int(width / target_ratio)
        if height > max_height:
            height = max_height
            width = int(height * target_ratio)

        self.setMinimumSize(600, 400)
        self.resize(int(width), int(height))

        if screen_geometry is not None:
            center_point = screen_geometry.center()
        else:
            center_point = self.frameGeometry().center()

        geometry = self.frameGeometry()
        geometry.moveCenter(center_point)
        self.move(geometry.topLeft())

        self.logger.debug(
            f"Window sized to ({width}x{height}) and centered"
        )

    def closeEvent(self, event):
        self.logger.debug("Close event triggered")

        message_box = QMessageBox(parent=self)
        message_box.setWindowTitle(self.tr("Exit?"))
        message_box.setText(self.tr("Are you sure you want to exit?"))
        message_box.setIcon(QMessageBox.Icon.Question)
        message_box.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        message_box.setDefaultButton(QMessageBox.StandardButton.No)

        result = message_box.exec()

        match result:
            case QMessageBox.StandardButton.Yes:
                self.logger.debug("User confirmed exit")
                event.accept()
            case QMessageBox.StandardButton.No:
                self.logger.debug("User canceled exit")
                event.ignore()

    def _on_page_error(self, exc: Exception):
        self.logger.error("Unhandled exception")

        log_path = Path(Logger().get_log_file_path())

        message_box = QMessageBox(parent=self)
        message_box.setIcon(QMessageBox.Icon.Critical)
        message_box.setWindowTitle(self.tr("Error"))
        message_box.setText(self.tr("An unexpected error has occurred."))
        message_box.setDetailedText(self.tr(
            f'Log file created at:\n{log_path.absolute().resolve()}'
        ))
        message_box.setStandardButtons(
            QMessageBox.StandardButton.Ok
            | QMessageBox.StandardButton.Open
        )
        message_box.setDefaultButton(QMessageBox.StandardButton.Open)

        QApplication.beep()
        result = message_box.exec()

        match result:
            case QMessageBox.StandardButton.Open:
                QDesktopServices.openUrl(QUrl.fromLocalFile(log_path))

        QApplication.exit(1)
        raise exc


class ScaledLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._pixmap = None
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setSizePolicy(QSizePolicy.Policy.Expanding,
                           QSizePolicy.Policy.Expanding)

    def setPixmap(self, pixmap: QPixmap):
        self._pixmap = pixmap
        super().setPixmap(pixmap)

    def resizeEvent(self, event):
        if self._pixmap:
            scaled = self._pixmap.scaled(
                QSize(
                    int(
                        self._pixmap.width()
                        * self.height()
                        / self._pixmap.height()
                    ),
                    self.height()),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            super().setPixmap(scaled)
        super().resizeEvent(event)
