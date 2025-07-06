import tkinter.ttk as ttk

from pages.base import BasePage

class SelectPathPage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        ttk.Label(self, text="Selecione o caminho").pack()
        ttk.Button(self, text="Voltar", command=lambda: controller.show_page("WelcomePage")).pack()