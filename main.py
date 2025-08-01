import gettext
import sys

from PySide6.QtCore import QUrl, QObject, QEvent
from PySide6.QtGui import QDesktopServices, Qt
from PySide6.QtWidgets import QApplication, QMessageBox, QPushButton
from app import App
from logger import _Logger

_ = gettext.gettext
LOG_PREFIX = "App:"

def excepthook(exc_type, exc_value, exc_tb):
    logger.exception(f"{LOG_PREFIX} Unhandled exception", exc_info=(exc_type, exc_value, exc_tb))
    log_path = _Logger.get_log_file_path()

    messagebox = QMessageBox()
    messagebox.setIcon(QMessageBox.Icon.Critical)
    messagebox.setWindowTitle(_("Erro"))
    messagebox.setText(_("Um erro inesperado aconteceu.\nArquivo de log criado."))
    messagebox.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Open)
    messagebox.setDefaultButton(QMessageBox.StandardButton.Open)
    QApplication.beep()
    result = messagebox.exec()

    match result:
        case QMessageBox.StandardButton.Open:
            QDesktopServices.openUrl(QUrl.fromLocalFile(log_path))

    logger.info(f"{LOG_PREFIX} Terminated")
    sys.exit(1)

sys.excepthook = excepthook

class ButtonDisableFilter(QObject):
    """
    This filter prevents the hover effect freeze after a QPushButton is set to disable.
    """
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.EnabledChange:
            if isinstance(obj, QPushButton) and not obj.isEnabled():
                obj.setAttribute(Qt.WidgetAttribute.WA_UnderMouse, False)
                obj.style().unpolish(obj)
                obj.style().polish(obj)
        return super().eventFilter(obj, event)


if __name__ == "__main__":
    logger = _Logger.get_logger()
    try:
        app = QApplication(sys.argv)
        app.installEventFilter(ButtonDisableFilter(app))
        main_window = App()
        main_window.show()
        sys.exit(app.exec())
    finally:
        logger.info(f"{LOG_PREFIX} Terminated")