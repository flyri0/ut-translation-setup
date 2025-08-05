import logging
import sys
import threading
from pathlib import Path

from src.utils import is_nuitka


class Logger:
    _lock = threading.Lock()
    _instance = None

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
        return cls._instance

    def __init__(
            self,
            name: str = "setup",
            level: int = logging.INFO,
    ):
        if getattr(self, "_initialized", False):
            return
        self._initialized = True

        log_dir = Path(__name__).parent.parent
        if is_nuitka():
            log_dir = Path(sys.executable).parent

        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / f"{name}.log"
        if log_file.exists():
            log_file.unlink()

        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        if not self.logger.handlers:
            fmt = logging.Formatter(
                "%(asctime)s"
                " [%(filename)s:%(lineno)d]"
                " %(levelname)s -"
                " %(message)s"
            )
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setFormatter(fmt)
            self.logger.addHandler(file_handler)

            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(fmt)
            self.logger.addHandler(stream_handler)

    def get_logger(self):
        return self.logger

    @classmethod
    def new(cls, name: str = "setup", level: int = logging.INFO):
        return cls(name=name, level=level).get_logger()
