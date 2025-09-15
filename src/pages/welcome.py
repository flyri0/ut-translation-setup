from PySide6.QtCore import Signal
from PySide6.QtGui import QPixmap, Qt
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QSizePolicy, \
    QVBoxLayout, QFrame, QPushButton


class WelcomePage(QWidget):
    finished = Signal()

    def __init__(self):
        super().__init__()
        self._ui()

    def _ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.banner = QPixmap(":banner")
        self.banner_label = QLabel()
        self.banner_label.setSizePolicy(
            QSizePolicy.Policy.Minimum,
            QSizePolicy.Policy.Ignored,
        )

        self.next_button = QPushButton()
        self.next_button.clicked.connect(self.finished.emit)
        self.next_button.setText(self.tr("Let's Go!"))
        self.next_button.setMinimumHeight(50)
        self.next_button.setDefault(True)
        self.next_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.next_button.setStyleSheet(
            """
            font-size: 15px;
            font-weight: bold;
            """
        )

        message = QLabel(
            f"""
                <h2>{self.tr("Until Then... <i>in portuguese!</i> ✨")}</h2>
                
                <p>
                {self.tr(
                "Thank you for being here!"
                " This translation was made with love"
                " by fans, so that more people can experience the story"
                " of <i>Until Then</i> in our language."
                " We hope it moves you as much as it moved us."
            )}
                </p>
                <br>
                <center>
                    <i>
                        {self.tr("Translation by:")}<br>
                        {self.tr("person · person · person · person")}<br><br>
                        
                        {self.tr("Installer by:")}<br>
                        <a href="https://github.com/flyri0">flyr0</a>
                        <br>
                    </i>
                    <br>
                    <a style="text-decoration: none;"
                        href=\"{self.tr("https://discord.gg/MKn6QBVG9g")}\">
                        Discord
                    </a>
                    ·
                    <a style="text-decoration: none;"
                        href=\"{self.tr("https://github.com/flyri0/ut-translation-setup")}\">
                        Github
                    </a>
                </center>
            """
        )
        message.setWordWrap(True)
        message.setOpenExternalLinks(True)
        message.setContentsMargins(10, 0, 10, 0)

        message_and_button_frame = QFrame()
        message_and_button_frame.setLayout(
            QVBoxLayout(message_and_button_frame)
        )
        message_and_button_frame.layout().addWidget(message)
        message_and_button_frame.layout().addWidget(self.next_button)

        layout.addWidget(self.banner_label)
        layout.addWidget(message_and_button_frame, 1)

        self._update_banner_size()

    def resizeEvent(self, event):
        super().resizeEvent(event)

        self._update_banner_size()

    def _update_banner_size(self):
        if self.banner.isNull():
            return

        available_size = self.banner_label.size()

        scaled_pixmap = self.banner.scaledToHeight(
            available_size.height(),
            Qt.TransformationMode.FastTransformation,
        )

        self.banner_label.setPixmap(scaled_pixmap)
