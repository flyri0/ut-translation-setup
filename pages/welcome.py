import gettext

from PySide6.QtCore import Qt, QMargins
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel, QHBoxLayout

from pages.base import BasePage

_ = gettext.gettext
LOG_PREFIX = "WelcomePage:"


class WelcomePage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        self.controller.logger.debug(f"{LOG_PREFIX} Loaded")
        self._original_pixmap = QPixmap(":/assets/banner.jpg")
        self._build_ui()

    def _build_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.banner_label = QLabel(self)

        # QLabel support some HTML tags: https://doc.qt.io/qt-6/richtext-html-subset.html
        message = QLabel(_(
            """
            <h2 align="left">Until Then... <i>In portuguese!</i></h2>
            
            <p align="left">
                Thank you for being here! This translation was made with love
                by fans, so that more people can experience the story of <i>Until Then</i>
                in our language, We hope you get as emotional as we did.
            </p>
            <br>
            <center><i>
                Translation by:<br>
                person · person · person · person<br><br>
                
                Installer by:<br>
                <a href="https://github.com/flyri0">flyr0</a>
                <br>
            </i></center>
            
            <center>
                <a href="https://discord.gg/MKn6QBVG9g">Discord</a>
                ·
                <a href="https://github.com/flyri0/ut-translation-setup">Github</a>
            </center>
            """
        ))
        message.setWordWrap(True)
        message.setOpenExternalLinks(True)
        message.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignCenter)
        message.setContentsMargins(QMargins(10, 0, 10, 0))

        main_layout.addWidget(self.banner_label)
        main_layout.addWidget(message, stretch=1)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if not self._original_pixmap.isNull():
            scaled_pixmap = self._original_pixmap.scaledToHeight(
                self.height(), Qt.SmoothTransformation
            )
            self.banner_label.setPixmap(scaled_pixmap)