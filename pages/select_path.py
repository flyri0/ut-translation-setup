import tkinter as tk
import tkinter.ttk as ttk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import AppController

class SelectPathPage(tk.Frame):
    def __init__(self, parent, controller: 'AppController'):
        super().__init__(parent)
        self.controller: 'AppController' = controller

        tk.Label(self, text="Selecione o caminho").pack()
        ttk.Button(self, text="Voltar", command=lambda: controller.show_page("WelcomePage")).pack()