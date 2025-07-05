import tkinter as tk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import AppController

class BasePage(tk.Frame):
    def __init__(self, parent, controller: 'AppController'):
        super().__init__(parent)
        self.controller = controller
