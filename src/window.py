from PySide6.QtWidgets import QMainWindow, QStackedWidget

from src.pages.verify_version import VerifyVersionPage


class AppWindow(QMainWindow):
    def __init__(self, config):
        super().__init__()

        self.config = config

        self.page_stack = QStackedWidget()
        self.verify_version_page = VerifyVersionPage(
            setup_version=config["setup_version"],
            repo_id=config["repository_id"]
        )

        self.page_stack.addWidget(self.verify_version_page)

        self.setCentralWidget(self.page_stack)
