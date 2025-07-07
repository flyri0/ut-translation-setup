import tkinter as tk
from tkinter import ttk

from pages.base import BasePage

# TODO: Literally everything, this is just a test :_)
class WelcomePage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        controller.logger.debug("WelcomePage: loaded")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0, minsize=200)
        self.grid_columnconfigure(1, weight=1)

        self.banner_label = tk.Label(self, background="red")
        self.banner_label.grid(row=0, column=0, sticky="nsew")

        label = ttk.Label(self, text="Bem-vindo ao UT-Translation")
        label.grid(row=0, column=1)
