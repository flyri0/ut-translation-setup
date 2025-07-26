import gettext
from typing import TYPE_CHECKING

from PySide6.QtGui import QShowEvent
from PySide6.QtWidgets import QWidget

if TYPE_CHECKING:
    from app import App

_ = gettext.gettext

class BasePage(QWidget):
    def __init__(self, parent, controller: 'App', window_title: str):
        super().__init__(parent)
        self.controller = controller
        self._window_title = window_title

    def showEvent(self, event: QShowEvent):
        super().showEvent(event)
        self.controller.setWindowTitle(_(f"{self._window_title} - Install Translation"))