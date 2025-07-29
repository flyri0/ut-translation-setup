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
        self.controller.logger.debug(f"{LOG_PREFIX} Page initialized")
        self._build_ui()
        self.controller.logger.debug(f"{LOG_PREFIX} UI built")

    def _build_ui(self):
        self.controller.logger.debug(f"{LOG_PREFIX} Building UI components")
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # QLabel supports HTML rich text
        message = QLabel(_(
            """
            <h2>Until Then... <i>em português!</i></h2>
            <p>
                Obrigado por estar aqui! Esta tradução foi feita com amor
                por fãs, para que mais pessoas possam conhecer a história de <i>Until Then</i>
                em nosso idioma. Esperamos que você se emocione tanto quanto nós.
            </p>
            <br>
            <center>
                <i>
                    Tradução feita por:<br>
                    person · person · person · person<br><br>

                    Instalador feito por:<br>
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
        self.controller.logger.debug(f"{LOG_PREFIX} Message label configured")

        socials = QLabel(_(
            """
                <div>
                    <a style="text-decoration: none;" href=\"https://discord.gg/MKn6QBVG9g\">\uf392 <!--discord icon in fontawesome--></a>
                    <a style="text-decoration: none;" href=\"https://github.com/flyri0/ut-translation-setup\">\uf09b <!--github icon in fontawesome--></a>
                </div>
            """
        ))
        socials.setAlignment(Qt.AlignmentFlag.AlignCenter)
        socials.setOpenExternalLinks(True)
        socials.setFont(qtawesome.font("fa6b", 26))
        self.controller.logger.debug(f"{LOG_PREFIX} Social links configured")

        message_frame = QFrame()
        message_frame.setLayout(QVBoxLayout(message_frame))
        message_frame.layout().addWidget(message)
        message_frame.layout().addWidget(socials)
        self.controller.logger.debug(f"{LOG_PREFIX} Message frame assembled")

        main_layout.addWidget(message_frame)
        self.controller.logger.debug(f"{LOG_PREFIX} Main layout assembled")

    def showEvent(self, event):
        super().showEvent(event)
        self.controller.logger.debug(f"{LOG_PREFIX} showEvent: configuring visibility and navigation")
        self.controller.banner.setVisible(True)
        self.controller.line.setVisible(True)
        self.controller.button_container.setVisible(True)

        self.controller.back_button.setEnabled(False)
        self.controller.next_button.setEnabled(True)
        self.controller.logger.debug(f"{LOG_PREFIX} Navigation buttons configured")
