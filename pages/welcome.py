import gettext

import qtawesome
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QHBoxLayout, QSizePolicy, QVBoxLayout, QFrame

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
            </center>
            """
        ))
        message.setWordWrap(True)
        message.setOpenExternalLinks(True)
        message.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        message.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        message.setContentsMargins(10, 0, 10, 0)

        socials = QLabel(_(
            """
                <div>
                    <a style="text-decoration: none;" href=\"https://discord.gg/Kv3XSDRR3H\">\uf392 <!--discord icon in fontawesome--></a>
                    <a style="text-decoration: none;" href=\"https://github.com/flyri0/ut-translation-setup\">\uf09b <!--github icon in fontawesome--></a>
                </div>
            """))
        socials.setAlignment(Qt.AlignmentFlag.AlignCenter)
        socials.setOpenExternalLinks(True)
        socials.setFont(qtawesome.font("fa6b", 26))

        message_frame = QFrame()
        message_frame.setLayout(QVBoxLayout(message_frame))
        message_frame.layout().addWidget(message)
        message_frame.layout().addWidget(socials)

        main_layout.addWidget(message_frame)