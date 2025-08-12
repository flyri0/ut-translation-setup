import sys

from PySide6.QtWidgets import QApplication

from src.app import App
from src.logger import Logger

if __name__ == "__main__":
    logger = Logger().get_logger()
    try:
        app = QApplication(sys.argv)

        main_window = App()
        main_window.show()
        sys.exit(app.exec())
    except Exception as error:
        logger.exception(error)
