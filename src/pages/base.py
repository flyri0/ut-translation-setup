from typing import TYPE_CHECKING

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget

from src.logger import Logger

if TYPE_CHECKING:
    from src.app import App


class BasePage(QWidget):
    error = Signal(Exception)

    def __init__(self, parent, controller: 'App'):
        super().__init__(parent)
        self.controller = controller
        self.logger = Logger().get_logger()
