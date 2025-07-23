import gettext
import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QStackedWidget, QFrame, QApplication, QPushButton, \
    QHBoxLayout, QMessageBox, QSizePolicy
from screeninfo import get_monitors

from logger import _Logger
from pages.select_game_path import SelectGamePath
from pages.welcome import WelcomePage
from state import AppState

import assets

_ = gettext.gettext
LOG_PREFIX = "App:"

class App(QMainWindow):
    def __init__(self):
        super().__init__()

        self.state = AppState()
        self.logger = _Logger.get_logger()
        self.logger.info(f"{LOG_PREFIX} Initialized")

        self.page_sequence = [WelcomePage, SelectGamePath]
        self.current_index: int = 0

        self._build_ui()
        self.setWindowIcon(QIcon(":/assets/icon.ico"))
        self.setWindowTitle(_("Until Then - Install Translation"))
        self._center_window()
        self._show_page(0)

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack, stretch=1)

        for page_cls in self.page_sequence:
            page = page_cls(parent=self, controller=self)
            self.stack.addWidget(page)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(line)

        button_layout = QHBoxLayout()

        self.cancel_button = QPushButton(_("Cancel"))
        self.back_button = QPushButton(_("Back"))
        self.next_button = QPushButton(_("Next"))

        self.cancel_button.clicked.connect(self._handle_exit)
        self.back_button.clicked.connect(self._previous_page)
        self.next_button.clicked.connect(self._next_page)

        button_layout.addWidget(self.cancel_button)
        button_layout.addStretch(1)
        button_layout.addWidget(self.back_button)
        button_layout.addWidget(self.next_button)

        button_container = QWidget()
        button_container.setLayout(button_layout)

        main_layout.addWidget(button_container)

    def _show_page(self, index: int):
        if not (0 <= index < self.stack.count()):
            self.logger.warning(f"{LOG_PREFIX} Page index {index} out of bounds")
            return

        self.stack.setCurrentIndex(index)
        self.current_index = index
        self.logger.info(f"{LOG_PREFIX} Page {type(self.stack.currentWidget()).__name__} displayed")
        self._update_navigation_buttons()

    def _next_page(self):
        self._show_page(self.current_index + 1)

    def _previous_page(self):
        self._show_page(self.current_index - 1)

    def _update_navigation_buttons(self):
        self.back_button.setEnabled(self.current_index > 0)
        self.next_button.setEnabled(self.current_index < self.stack.count() - 1)

    def _handle_exit(self):
        self.logger.info(f"{LOG_PREFIX} Termination requested by user")
        reply = QMessageBox.question(
            self,
            _("Exit"),
            _("Are you sure you want to exit?"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.close()
        else:
            self.logger.info(f"{LOG_PREFIX} Termination aborted by user")

    def _center_window(self):
        for monitor in get_monitors():
            if monitor.is_primary:
                screen_w, screen_h = monitor.width, monitor.height
                break
        else:
            screen_w, screen_h = 1280, 720

        width = int(screen_w * 0.35)
        height = int(screen_h * 0.5)
        self.resize(width, height)

        geo = self.frameGeometry()
        center = self.screen().availableGeometry().center()
        geo.moveCenter(center)
        self.move(geo.topLeft())

if __name__ == "__main__":
    logger = _Logger.get_logger()
    try:
        app = QApplication([])
        main_window = App()
        main_window.show()
        sys.exit(app.exec())
    except Exception:
        logger.exception(f"{LOG_PREFIX} Unhandled exception occurred during runtime")
        QMessageBox.critical(
            None,
            _("Error"),
            _(f"An unexpected error has occurred.\nA log file was generated at: {_Logger.get_log_file_path()}"),
            QMessageBox.StandardButton.Ok
        )
    finally:
        if logger:
            logger.info(f"{LOG_PREFIX} Terminated")