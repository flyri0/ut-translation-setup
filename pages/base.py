import gettext
from typing import TYPE_CHECKING

from PySide6.QtWidgets import QWidget

if TYPE_CHECKING:
    from app import App

_ = gettext.gettext

class BasePage(QWidget):
    def __init__(self, parent, controller: 'App'):
        super().__init__(parent)
        self.controller = controller