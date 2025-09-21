from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class FinalPage(QWidget):
    def __init__(self):
        super().__init__()

        self._ui()

    def _ui(self):
        layout = QVBoxLayout(self)

        label = QLabel(self)
        label.setText(self.tr("Final Page"))

        layout.addWidget(label)
