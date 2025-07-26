import gettext

from PySide6.QtWidgets import QVBoxLayout, QLabel

from pages.base import BasePage

_ = gettext.gettext

LOG_PREFIX = "FetchTranslationFiles:"

class FetchTranslationFilesPage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        self.controller.logger.debug(f"{LOG_PREFIX} Loaded")
        self._build_ui()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(QLabel(self.__class__.__name__))