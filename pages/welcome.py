import gettext

from PySide6.QtCore import Qt, QMargins, QSize
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel, QHBoxLayout, QSizePolicy

from pages.base import BasePage

_ = gettext.gettext
LOG_PREFIX = "WelcomePage:"


class WelcomePage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        self.controller.logger.debug(f"{LOG_PREFIX} Loaded")
        self._build_ui()

    def _build_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # QLabel support some HTML tags: https://doc.qt.io/qt-6/richtext-html-subset.html
        message = QLabel(_(
            """
            <h2>Until Then... <i>In portuguese!</i></h2>
            <p>
                Thank you for being here! This translation was made with love
                by fans, so that more people can experience the story of <i>Until Then</i>
                in our language, We hope you get as emotional as we did.
            </p>
            <br>
            <center>
                <i>
                    Translation by:<br>
                    person · person · person · person<br><br>
                    
                    Installer by:<br>
                    <a href="https://github.com/flyri0">flyr0</a>
                    <br>
                </i>
                <br>
                <a href="https://discord.gg/MKn6QBVG9g">Discord</a>
                ·
                <a href="https://github.com/flyri0/ut-translation-setup">Github</a>
            </center>
            """
        ))
        message.setWordWrap(True)
        message.setOpenExternalLinks(True)
        message.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        message.setContentsMargins(QMargins(10, 0, 10, 0))

        banner = ScaledLabel()
        banner.setPixmap(QPixmap(":/assets/banner.jpg"))

        main_layout.addWidget(banner)
        main_layout.addWidget(message, stretch=1)

class ScaledLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._pixmap = None
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )

    def setPixmap(self, pixmap: QPixmap):
        self._pixmap = pixmap
        super().setPixmap(pixmap)


    def resizeEvent(self, event):
        if self._pixmap:
            scaled = self._pixmap.scaled(
                QSize(int(self._pixmap.width() * self.height() / self._pixmap.height()), self.height()),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            super().setPixmap(scaled)
        super().resizeEvent(event)