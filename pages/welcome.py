import tkinter as tk
import tkinter.ttk as ttk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import AppController

class WelcomePage(tk.Frame):
    def __init__(self, parent, controller: 'AppController'):
        super().__init__(parent)
        self.controller: 'AppController' = controller

        tk.Label(self, text="Bem-vindo").pack()

        ttk.Button(self, text="Próximo", command=lambda: controller.show_page("SelectPathPage")).pack()