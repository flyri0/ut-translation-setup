from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QTemporaryDir


@dataclass
class AppState:
    game_path: Optional[Path] = None
    is_demo: Optional[bool] = None
    _temp_dir: Path = field(init=False, repr=False)

    def __post_init__(self):
        self._qtemp_dir = QTemporaryDir()
        if not self._qtemp_dir.isValid():
            raise RuntimeError("Failed to create temporary directory")

        self._temp_dir = Path(self._qtemp_dir.path())

    @property
    def temp_dir(self) -> Path:
        return self._temp_dir