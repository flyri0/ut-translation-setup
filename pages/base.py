import tkinter.ttk as ttk
from typing import TYPE_CHECKING

from logger import AppLogger

if TYPE_CHECKING:
    from main import AppController

class BasePage(ttk.Frame):
    def __init__(self, parent, controller: 'AppController'):
        super().__init__(parent)
        self.controller = controller
        self.logger = AppLogger.get_logger()
