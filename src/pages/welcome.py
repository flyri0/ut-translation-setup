import qtawesome
from PySide6.QtGui import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QFrame, QVBoxLayout

from src.pages.base import BasePage


class WelcomePage(BasePage):
    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        message = QLabel(
            f"""
            <h2>{self.tr("Until Then... <i>in portuguese!</i>")}</h2>
            <p>
            {self.tr(
                "Thank you for being here! This translation was made with love"
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
            </center>
            """
        )
        message.setWordWrap(True)
        message.setOpenExternalLinks(True)
        message.setAlignment(
            Qt.AlignmentFlag.AlignVCenter
            | Qt.AlignmentFlag.AlignLeft
        )
        message.setContentsMargins(10, 0, 10, 0)

        socials = QLabel(
            f"""
                <div>
                    <a style="text-decoration: none;"
                        href=\"{self.tr("https://discord.gg/MKn6QBVG9g")}\">
                        \uf392 <!--discord icon in fontawesome-->
                    </a>
                    <a style="text-decoration: none;"
                        href=\"{self.tr("https://github.com/flyri0/ut-translation-setup")}\">
                        \uf09b <!--github icon in fontawesome-->
                    </a>
                </div>
            """
        )
        socials.setAlignment(Qt.AlignmentFlag.AlignCenter)
        socials.setOpenExternalLinks(True)
        socials.setFont(qtawesome.font("fa6b", 26))

        message_frame = QFrame()
        message_frame.setLayout(QVBoxLayout(message_frame))
        message_frame.layout().addWidget(message)
        message_frame.layout().addWidget(socials)

        layout.addWidget(message_frame)

    def showEvent(self, event):
        super().showEvent(event)

        self.controller.banner.setVisible(True)
        self.controller.line.setVisible(True)
        self.controller.button_container.setVisible(True)

        self.controller.back_button.setEnabled(False)
        self.controller.next_button.setEnabled(True)
