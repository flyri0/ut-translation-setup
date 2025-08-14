import socket

import semver
from PySide6.QtCore import QThread, QObject, Signal, Qt, QTimer, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QVBoxLayout, QLabel, QProgressBar, QMessageBox, \
    QApplication
from github import Github, GithubException

from src.pages.base import BasePage


class VerifyVersionPage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        self.thread = QThread(self)
        self.worker = _Worker(
            self.controller.state.installer_version,
            self.controller.state.github_repo_id,
        )
        self.worker.moveToThread(self.thread)

        self.worker.status.connect(self._on_status)
        self.worker.no_internet.connect(self._handle_no_internet)
        self.worker.error.connect(self._on_error)
        self.worker.update_available.connect(self._handle_update_available)
        self.worker.up_to_date.connect(self._on_up_to_date)
        self.worker.finished.connect(self.thread.quit)
        self.thread.started.connect(self.worker.run)

        self.show()
        self.thread.start()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(30, 0, 30, 0)

        self.status = QLabel()
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)

        progressbar = QProgressBar()
        progressbar.setRange(0, 0)
        progressbar.setTextVisible(False)

        layout.addWidget(self.status)
        layout.addWidget(progressbar)

        self.no_internet_msg = QMessageBox(parent=self.controller)
        self.no_internet_msg.setIcon(QMessageBox.Icon.Warning)
        self.no_internet_msg.setWindowTitle(self.tr("No internet connection"))
        self.no_internet_msg.setText(self.tr(
            "You are not connected to the internet. "
            "Please check your internet connection and try again "
            "or do you want to continue anyway?"
        ))
        self.no_internet_msg.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Retry
        )
        self.no_internet_msg.setDefaultButton(QMessageBox.StandardButton.Retry)

        self.update_available_msg = QMessageBox(parent=self.controller)
        self.update_available_msg.setIcon(QMessageBox.Icon.Information)
        self.update_available_msg.setWindowTitle(self.tr("Update available"))
        self.update_available_msg.setText(self.tr(
            "Translation update available, do you wish to download now?"
        ))
        self.update_available_msg.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        self.update_available_msg.setDefaultButton(
            QMessageBox.StandardButton.Yes
        )

    def _on_status(self, status):
        self.status.setText(status)

    def _handle_no_internet(self):
        self.controller.logger.warning("No internet detected")
        result = self.no_internet_msg.exec()
        if result == QMessageBox.StandardButton.Yes:
            self.controller.logger.info(
                "User chose to continue offline"
            )
            self.thread.quit()
            self.controller.next_page()
        elif result == QMessageBox.StandardButton.Retry:
            self.controller.logger.info("User chose to retry internet check")
            QTimer.singleShot(0, self.thread.start)

    def _on_error(self, error):
        self.controller.logger.error(
            "Error fetching release info, proceeding without check"
        )
        self.controller.logger.error(error)
        self.thread.quit()
        self.controller.next_page()

    def _handle_update_available(self, latest_tag, url):
        answer = self.update_available_msg.exec()
        if answer == QMessageBox.StandardButton.Yes:
            self.controller.logger.info(
                "Opening URL {url} and exiting")
            QDesktopServices.openUrl(QUrl(url))
            QApplication.quit()
        else:
            self.controller.logger.info(
                "User declined update, continuing")
            self.controller.next_page()

    def _on_up_to_date(self):
        self.controller.logger.debug(
            "Installer version is up-to-date"
        )
        self.controller.next_page()

    def showEvent(self, event):
        super().showEvent(event)
        self.controller.banner.setVisible(False)
        self.controller.button_container.setVisible(False)
        self.controller.line.setVisible(False)


class _Worker(QObject):
    status = Signal(str)
    no_internet = Signal()
    up_to_date = Signal()
    update_available = Signal(str, str)
    error = Signal(Exception)
    finished = Signal()

    def __init__(self, installer_version, github_repo_id, parent=None):
        super().__init__(parent)
        self.installer_version = installer_version
        self.github_repo_id = github_repo_id

    def run(self):
        self.status.emit(self.tr("Checking internet connection..."))
        if not self.is_connected():
            self.no_internet.emit()
            self.finished.emit()
            return

        self.status.emit(self.tr("Checking for updates..."))

        try:
            repo = Github().get_repo(self.github_repo_id)
            latest_tag = repo.get_latest_release().tag_name
        except GithubException as error:
            self.error.emit(error)
            self.finished.emit()
            return

        if semver.compare(self.installer_version, latest_tag) < 0:
            url = f"https://github.com/{repo.full_name}/releases"
            self.update_available.emit(latest_tag, url)
        else:
            self.up_to_date.emit()
        self.finished.emit()

    @staticmethod
    def is_connected():
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
                socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(
                    (host, port))
                return True
            except socket.error:
                continue
        return False
