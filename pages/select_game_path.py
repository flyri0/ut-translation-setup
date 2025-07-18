import tkinter.ttk as ttk
import tkinter as tk
from tkinter import font

from pages.base import BasePage

# TODO: Everything
class SelectGamePathPage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        controller.logger.debug("SelectGamePathPage: loaded")
        controller.back_button.configure(state="enabled")

        selected_path_frame = ttk.Frame(self)
        selected_path_frame.pack(fill="x", expand=True)
        selected_path_frame.columnconfigure(0, weight=1)

        self.path_label = ttk.Label(selected_path_frame, borderwidth=1, relief="solid")
        self.path_label.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        self.select_path_button = ttk.Button(selected_path_frame, text="Selecionar")
        self.select_path_button.grid(row=0, column=1)

        self.status_label = ttk.Label(selected_path_frame, text="UntilThen.exe não foi encontrado.", foreground="red")
        self.status_label.grid(row=1, column=0, columnspan=2, sticky="w", pady=(5, 0))
