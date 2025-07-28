import gettext
import sys

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QApplication, QMessageBox
from app import App
from logger import _Logger

_ = gettext.gettext
LOG_PREFIX = "App:"

def excepthook(exc_type, exc_value, exc_tb):
    logger.exception(f"{LOG_PREFIX} Unhandled exception", exc_info=(exc_type, exc_value, exc_tb))
    log_path = _Logger.get_log_file_path()

    messagebox = QMessageBox()
    messagebox.setIcon(QMessageBox.Icon.Critical)
    messagebox.setWindowTitle(_("Erro Inesperado"))
    messagebox.setText(_("Um arquivo de log foi criado."))
    messagebox.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Open)
    messagebox.setButtonText(QMessageBox.StandardButton.Open, _("Abrir"))
    messagebox.setDefaultButton(QMessageBox.StandardButton.Open)
    QApplication.beep()
    result = messagebox.exec()

    match result:
        case QMessageBox.StandardButton.Open:
            QDesktopServices.openUrl(QUrl.fromLocalFile(log_path))

    logger.info(f"{LOG_PREFIX} Terminated")
    sys.exit(1)

sys.excepthook = excepthook

if __name__ == "__main__":
    logger = _Logger.get_logger()
    try:
        app = QApplication(sys.argv)
        main_window = App()
        main_window.show()
        sys.exit(app.exec())
    finally:
        logger.info(f"{LOG_PREFIX} Terminated")