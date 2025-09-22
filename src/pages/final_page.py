from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QMovie
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy, \
    QPushButton


class FinalPage(QWidget):
    quit = Signal()

    def __init__(self):
        super().__init__()

        self._ui()

    def _ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(150, 0, 150, 0)

        message = QLabel(self)
        message.setWordWrap(True)
        message.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        message.setText(self.tr(
            f"""
            <center>
             <h1>{self.tr("Installation complete! 🎉")}</h1>
             <p>{self.tr("""
                Now it’s your turn to dive into this journey.
                We hope every moment of <i>Until Then</i> touches you deeply,
                just as it touched us while bringing it to you.
             """)}</p>
             </center>
            """
        ))

        gif_movie = QMovie(":cathy")
        gif_movie.start()
        gif_movie.setScaledSize(QSize(100, 100))

        gif_label = QLabel()
        gif_label.setMovie(gif_movie)
        gif_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.close_button = QPushButton(self.tr("Close"))
        self.close_button.setMinimumHeight(50)
        self.close_button.clicked.connect(self._on_close)
        self.close_button.setStyleSheet(
            """
            font-size: 15px;
            font-weight: bold;
            """
        )

        layout.addStretch()
        layout.addWidget(gif_label)
        layout.addWidget(message)
        layout.addWidget(self.close_button)
        layout.addStretch()

    def _on_close(self):
        self.quit.emit()
