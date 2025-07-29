import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QTemporaryDir
from dotenv import load_dotenv


@dataclass
class AppState:
    game_path: Optional[Path] = None
    is_demo: Optional[bool] = None
    _temp_dir: Path = field(init=False, repr=False)
    _installer_version: Optional[str] = None
    _github_repo_id: Optional[int] = None

    def __post_init__(self):
        load_dotenv()
        self._qtemp_dir = QTemporaryDir()
        if not self._qtemp_dir.isValid():
            raise RuntimeError("Failed to create temporary directory")

        self._temp_dir = Path(self._qtemp_dir.path())
        self._installer_version = os.getenv("SETUP_VERSION")
        self._github_repo_id = os.getenv("REPO_ID")


    @property
    def temp_dir(self) -> Path:
        return self._temp_dir

    @property
    def installer_version(self):
        return self._installer_version

    @property
    def github_repo_id(self):
        return self._github_repo_id