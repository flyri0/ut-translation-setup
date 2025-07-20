import ttkbootstrap as ttk
from typing import TYPE_CHECKING

from logger import AppLogger

if TYPE_CHECKING:
    from main import App

class BasePage(ttk.Frame):
    def __init__(self, parent, controller: 'App'):
        super().__init__(parent)
        self.controller = controller
        self.logger = AppLogger.get_logger()
