import socket

import semver
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QMessageBox, QProgressBar, QApplication
from github import Github, GithubException


class VerifyVersionPage(QWidget):
    hide_controls = Signal()
    finished = Signal()

    def __init__(self, setup_version: str, repo_id: str):
        super().__init__()

        self.setup_version = setup_version
        self.repo_id = repo_id

        self.hide_controls.emit()
        self._ui()

        self.show()  # waits the first event loop
        self._verify_connection()
        self._verify_version()

    def _ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(150, 0, 150, 0)

        self.status = QLabel()
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)

        progress_bar = QProgressBar()
        progress_bar.setRange(0, 0)


        layout.addWidget(self.status)
        layout.addWidget(progress_bar)

        self.no_internet_msg = QMessageBox(parent=self)
        self.no_internet_msg.setIcon(QMessageBox.Icon.Warning)
        self.no_internet_msg.setWindowTitle(self.tr("No internet connection"))
        self.no_internet_msg.setText(self.tr(
            "You are not connected to the internet. "
            "Please check your internet connection and try again."
        ))
        self.no_internet_msg.setStandardButtons(
            QMessageBox.StandardButton.Cancel
            | QMessageBox.StandardButton.Retry
        )
        self.no_internet_msg.setDefaultButton(QMessageBox.StandardButton.Retry)

        self.update_available_msg = QMessageBox(parent=self)
        self.update_available_msg.setIcon(QMessageBox.Icon.Information)
        self.update_available_msg.setWindowTitle(self.tr("Update available"))
        self.update_available_msg.setText(self.tr(
            "A new translation update is available. "
            "Do you wish to download now?"
        ))
        self.update_available_msg.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        self.update_available_msg.setDefaultButton(QMessageBox.StandardButton.Yes)

    def _verify_version(self):
        self.status.setText(self.tr("Verifying translation version..."))

        try:
            repo = Github().get_repo(self.repo_id)
            latest_tag = repo.get_latest_release().tag_name
        except GithubException:
            self.finished.emit()
            return None

        if semver.compare(self.setup_version, latest_tag) < 0:
            url = f"https://github.com/{repo.full_name}/releases"
            result = self.update_available_msg.exec()

            if result == QMessageBox.StandardButton.Yes:
                QDesktopServices.openUrl(url)
                QApplication.quit()
            else:
                self.finished.emit()
                return None

        return None



    def _verify_connection(self):
        self.status.setText(self.tr("Verifying internet connection..."))

        if not self.is_connected():
            result = self.no_internet_msg.exec()

            if result == QMessageBox.StandardButton.Cancel:
                self.finished.emit()
                return None
            else:
                self._verify_connection()

        return None

    @staticmethod
    def is_connected() -> bool:
        skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        skt.settimeout(3)
        test_hosts = [
            ("1.1.1.1", 53),
            ("208.67.222.222", 53),
            ("114.114.114.114", 53),
            ("9.9.9.9", 53),
            ("www.baidu.com", 80),
        ]

        for host, port in test_hosts:
            try:
                skt.connect((host, port))
                return True
            except socket.error:
                continue
            finally:
                skt.close()

        return False
