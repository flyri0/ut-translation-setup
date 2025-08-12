from PySide6.QtCore import QResource
from PySide6.QtWidgets import QMainWindow

from src.logger import Logger


class App(QMainWindow):
    def __init__(self):
        super().__init__()

        self.logger = Logger().get_logger()

        QResource.registerResource('src/resources.rcc')

        self.logger.info("Application Initialized")
