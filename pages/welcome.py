from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout

class WelcomePage(QWidget):
    def __init__(self, parent=None, controller=None):
        super().__init__(parent)
        self.controller = controller
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        label = QLabel("Welcome Page")
        layout.addWidget(label)
