import gettext
import socket
import semver
from PySide6.QtCore import QObject, Signal, QThread, QTimer, QUrl, Qt
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QLabel, QVBoxLayout, QProgressBar, QMessageBox, QApplication
from github import Github, GithubException
from pages.base import BasePage

_ = gettext.gettext
LOG_PREFIX = "VerifyVersionPage:"
REPO_ID = 1014041717

class VerifyVersionPage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.controller.logger.debug(f"{LOG_PREFIX} Page initialized")
        self._build_ui()
        self.controller.logger.debug(f"{LOG_PREFIX} UI built")

        self.controller.logger.debug(f"{LOG_PREFIX} Setting up worker thread")
        self.thread = QThread(self)
        self.worker = VerifyVersionWorker(self.controller.state.installer_version)
        self.worker.moveToThread(self.thread)

        self.worker.started.connect(self._on_worker_started)
        self.worker.no_internet.connect(self._handle_no_internet)
        self.worker.error.connect(self._on_error)
        self.worker.update_available.connect(self._handle_update_available)
        self.worker.up_to_date.connect(self._on_up_to_date)
        self.worker.finished.connect(self.thread.quit)
        self.thread.started.connect(self.worker.run)

        self.show()
        self.thread.start()
        self.controller.logger.debug(f"{LOG_PREFIX} Worker thread started")

    def _build_ui(self):
        self.controller.logger.debug(f"{LOG_PREFIX} Building UI components")
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.status = QLabel()
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)

        progressbar = QProgressBar()
        progressbar.setRange(0, 0)
        progressbar.setTextVisible(False)

        layout.addWidget(self.status)
        layout.addWidget(progressbar)

        self.no_internet_connection_msg = QMessageBox(parent=self.controller)
        self.no_internet_connection_msg.setIcon(QMessageBox.Icon.Warning)
        self.no_internet_connection_msg.setWindowTitle(_("Sem conexão"))
        self.no_internet_connection_msg.setText(_(
            "Não foi possível verificar a versão mais recente da tradução.\nDeseja continuar mesmo assim?"
        ))
        self.no_internet_connection_msg.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Retry
        )
        self.no_internet_connection_msg.setDefaultButton(
            QMessageBox.StandardButton.Retry
        )

        self.update_available_msg = QMessageBox(parent=self.controller)
        self.update_available_msg.setIcon(QMessageBox.Icon.Information)
        self.update_available_msg.setWindowTitle(_("Nova versão disponível"))
        self.update_available_msg.setText(_(
            "Uma nova versão da tradução está disponível.\nDeseja baixá-la agora?"
        ))
        self.update_available_msg.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        self.update_available_msg.setDefaultButton(
            QMessageBox.StandardButton.Yes
        )
        self.controller.logger.debug(f"{LOG_PREFIX} Dialogs configured")

    def _on_worker_started(self):
        self.controller.logger.debug(f"{LOG_PREFIX} Worker started: checking internet")
        self.status.setText(_("Verificando versão da tradução..."))

    def _handle_no_internet(self):
        self.controller.logger.warning(f"{LOG_PREFIX} No internet detected")
        answer = self.no_internet_connection_msg.exec()
        if answer == QMessageBox.StandardButton.Yes:
            self.controller.logger.info(f"{LOG_PREFIX} User chose to continue offline")
            self.thread.quit()
            self.controller.next_page()
        else:
            self.controller.logger.info(f"{LOG_PREFIX} User chose to retry internet check")
            QTimer.singleShot(0, self.thread.start)

    def _on_error(self):
        self.controller.logger.error(f"{LOG_PREFIX} Error fetching release info, proceeding without check")
        self.controller.next_page()

    def _handle_update_available(self, repo_full_name: str, url: str):
        self.controller.logger.info(f"{LOG_PREFIX} Update available at {repo_full_name}")
        answer = self.update_available_msg.exec()
        if answer == QMessageBox.StandardButton.Yes:
            self.controller.logger.info(f"{LOG_PREFIX} Opening URL {url} and exiting")
            QDesktopServices.openUrl(QUrl(url))
            QApplication.quit()
        else:
            self.controller.logger.info(f"{LOG_PREFIX} User declined update, continuing")
            self.controller.next_page()

    def _on_up_to_date(self):
        self.controller.logger.debug(f"{LOG_PREFIX} Installer version is up-to-date")
        self.controller.next_page()

    def showEvent(self, event):
        super().showEvent(event)
        self.controller.logger.debug(f"{LOG_PREFIX} showEvent: hiding UI controls")
        self.controller.banner.setVisible(False)
        self.controller.button_container.setVisible(False)
        self.controller.line.setVisible(False)


class VerifyVersionWorker(QObject):
    started = Signal()
    no_internet = Signal()
    up_to_date = Signal()
    update_available = Signal(str, str)
    error = Signal()
    finished = Signal()

    def __init__(self, local_version: str, parent=None):
        super().__init__(parent)
        self.local_version = local_version

    def run(self):
        self.started.emit()
        if not self.is_connected():
            self.no_internet.emit()
            self.finished.emit()
            return
        self.started.emit()

        try:
            repo = Github().get_repo(REPO_ID)
            latest_tag = repo.get_latest_release().tag_name
        except GithubException as e:
            self.error.emit()
            self.finished.emit()
            return

        if semver.compare(self.local_version, latest_tag) < 0:
            url = f"https://github.com/{repo.full_name}/releases"
            self.update_available.emit(repo.full_name, url)
        else:
            self.up_to_date.emit()
        self.finished.emit()

    @staticmethod
    def is_connected() -> bool:
        test_hosts = [
            ("1.1.1.1", 53),
            ("208.67.222.222", 53),
            ("114.114.114.114", 53),
            ("9.9.9.9", 53),
            ("www.baidu.com", 80),
        ]
        for host, port in test_hosts:
            try:
                socket.setdefaulttimeout(3)
                socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
                return True
            except socket.error:
                continue
        return False
