from math import floor
from pathlib import Path

from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QMainWindow, QStackedWidget

from src.pages.install_files import InstallFilesPage
from src.pages.pick_target import PickTargetPage
from src.pages.verify_version import VerifyVersionPage
from src.pages.welcome import WelcomePage


class AppWindow(QMainWindow):
    def __init__(self, config):
        super().__init__()

        self.config = config
        self.setWindowIcon(QIcon(":icon"))
        self.setWindowTitle(self.tr("Until Then - Install Translation"))

        screen_size = self.screen().availableGeometry()
        self.resize(self._resize_with_ratio(
            screen_size.width(),
            screen_size.height(),
            (4, 3)
        ))

        self.page_stack = QStackedWidget()
        self.verify_version_page = VerifyVersionPage(
            setup_version=config["setup_version"],
            repo_name=config["repository_full_name"]
        )
        self.welcome_page = WelcomePage()
        self.pick_target_page = PickTargetPage()
        self.install_files_page = InstallFilesPage()

        self._connect_signals()

        self.page_stack.addWidget(self.verify_version_page)
        self.page_stack.addWidget(self.welcome_page)
        self.page_stack.addWidget(self.pick_target_page)
        self.page_stack.addWidget(self.install_files_page)

        self.setCentralWidget(self.page_stack)

    def _connect_signals(self):
        self.verify_version_page.quit.connect(self._on_quit)
        self.verify_version_page.finished.connect(
            self._on_finished
        )

        self.welcome_page.finished.connect(self._next_page)

        self.pick_target_page.finished.connect(self._on_pick_target_finished)

    def _on_pick_target_finished(self, target_path: Path, is_demo: bool):
        self.install_files_page.set_target_path(target_path)
        self.install_files_page.set_is_demo(is_demo)
        self._next_page()

    def _on_quit(self):
        self.close()

    def _on_finished(self):
        self._next_page()

    def _next_page(self):
        index = self.page_stack.currentIndex()
        count = self.page_stack.count()
        if index < count - 1:
            self.page_stack.setCurrentIndex(index + 1)

    @staticmethod
    def _resize_with_ratio(
            screen_width: int,
            screen_height: int,
            ratio: tuple[int, int],
            fraction: float = 0.5
    ):
        """
        Resize to be as large as possible up to `fraction` of the given screen
        size, while preserving the given aspect ratio (ratio[0]:ratio[1]).
        Returns a QSize(width, height).
        """

        max_w = screen_width * fraction
        max_h = screen_height * fraction

        ratio_w, ratio_h = ratio
        aspect = ratio_w / ratio_h

        width, height = max_w, max_w / aspect
        if height > max_h:
            height, width = max_h, max_h * aspect

        return QSize(int(floor(width)), int(floor(height)))
