from pathlib import Path
from typing import Optional

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget


class InstallFilesPage(QWidget):
    finished = Signal()

    def __init__(self):
        super().__init__()
        self._target_path: Optional[Path] = None
        self._is_demo: Optional[bool] = None

    def set_target_path(self, target_path: Path):
        self._target_path = target_path

    def set_is_demo(self, is_demo: bool):
        self._is_demo = is_demo
