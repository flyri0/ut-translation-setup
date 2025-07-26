import gettext
import sys

from PySide6.QtWidgets import QApplication, QMessageBox

from app import App
from logger import _Logger

_ = gettext.gettext

LOG_PREFIX = "App:"

if __name__ == "__main__":
    logger = _Logger.get_logger()
    try:
        app = QApplication([])
        main_window = App()
        main_window.show()
        sys.exit(app.exec())
    except Exception:
        logger.exception(f"{LOG_PREFIX} Unhandled exception occurred during runtime")
        QMessageBox.critical(
            None,
            _("Error"),
            _(f"An unexpected error has occurred.\nA log file was generated at: {_Logger.get_log_file_path()}"),
            QMessageBox.StandardButton.Ok
        )
    finally:
        if logger:
            logger.info(f"{LOG_PREFIX} Terminated")