import logging
import sys
import threading
from pathlib import Path
from typing import Optional, Union

from src.utils import is_nuitka


class Logger:
    _lock = threading.Lock()
    _instance: Optional["Logger"] = None

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
        return cls._instance

    def __init__(
        self,
        name: str = "setup",
        level: int = logging.DEBUG,
        log_dir: Optional[Union[str, Path]] = None,
    ):
        if getattr(self, "_initialized", False):
            return
        self._initialized = True

        if log_dir:
            base = Path(log_dir)
        else:
            base = Path(__name__).parent.parent

        if is_nuitka():
            base = Path(sys.executable).parent

        base.mkdir(parents=True, exist_ok=True)

        self._log_file: Path = (base / f"{name}.log").resolve()

        if self._log_file.exists():
            self._log_file.unlink()

        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        if not self.logger.handlers:
            fmt = logging.Formatter(
                "%(asctime)s"
                " [%(filename)s:%(lineno)d]"
                " %(levelname)s -"
                " %(message)s"
            )
            file_handler = logging.FileHandler(str(self._log_file), encoding="utf-8")
            file_handler.setFormatter(fmt)
            self.logger.addHandler(file_handler)

            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(fmt)
            self.logger.addHandler(stream_handler)

    def get_logger(self) -> logging.Logger:
        return self.logger

    def get_log_file_path(self) -> str:
        path = getattr(self, "_log_file", None)
        if path is None:
            raise RuntimeError(
                "Logger not initialized; no log file available."
            )
        return str(path)
