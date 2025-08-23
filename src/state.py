import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


@dataclass
class State:
    pck_path: Optional[Path] = None
    is_demo: Optional[bool] = None
    is_valid_file: bool = False
    _temp_dir: Path = field(init=False, repr=False)
    _temp_dir_mgr: Optional[tempfile.TemporaryDirectory] = field(init=False, repr=False, default=None)
    _installer_version: Optional[str] = field(init=False, repr=False, default=None)
    _github_repo_id: Optional[str] = field(init=False, repr=False, default=None)

    def __post_init__(self):
        load_dotenv()
        self._temp_dir_mgr = tempfile.TemporaryDirectory()
        self._temp_dir = Path(self._temp_dir_mgr.name)
        self._installer_version = os.getenv("SETUP_VERSION")
        self._github_repo_id = os.getenv("REPO_ID")

    @property
    def temp_dir(self) -> Path:
        return self._temp_dir

    @property
    def installer_version(self) -> Optional[str]:
        return self._installer_version

    @property
    def github_repo_id(self) -> Optional[str]:
        return self._github_repo_id

    def cleanup(self) -> None:
        if self._temp_dir_mgr is not None:
            try:
                self._temp_dir_mgr.cleanup()
            finally:
                self._temp_dir_mgr = None
