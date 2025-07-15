import tkinter.ttk as ttk

from pages.base import BasePage

# TODO: Everything
class SelectGamePathPage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        controller.logger.debug("SelectGamePathPage: loaded")
        controller.back_button.configure(state="enabled")

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        content = ttk.Frame(self)
        content.grid(row=0, column=0)
        content.columnconfigure(0, weight=1)

        ttk.Label(content, text="Caminho do jogo").grid(row=0, column=0, sticky="w", padx=5)

        ttk.Entry(content, state="readonly", width=40).grid(row=1, column=0, sticky="ew", padx=5, pady=2)

        ttk.Button(content, text="Selecionar").grid(row=1, column=1, sticky="w", padx=5, pady=2)

        ttk.Label(content, text="UntilThen.exe encontrado", foreground="green").grid(
            row=2, column=0, columnspan=2, sticky="w", padx=5
        )
