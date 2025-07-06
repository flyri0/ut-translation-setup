import tkinter.ttk as ttk

from pages.base import BasePage

class WelcomePage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        ttk.Label(self, text="Bem-vindo").pack()
