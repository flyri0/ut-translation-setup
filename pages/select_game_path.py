import tkinter.ttk as ttk

from pages.base import BasePage

class SelectGamePathPage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        controller.logger.debug("SelectGamePathPage: loaded")
        controller.back_button.configure(state="enabled")

        ttk.Label(self, text="Selecione o caminho").pack()