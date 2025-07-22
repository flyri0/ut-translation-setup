import logging
import pathlib
import sys
from datetime import datetime
from typing import Optional


class _Logger:
    _logger: Optional[logging.Logger] = None
    _log_file_path: Optional[pathlib.Path] = None

    @classmethod
    def get_logger(cls) -> logging.Logger:
        if cls._logger is None:
            cls._logger = logging.getLogger("_Logger")
            cls._logger.setLevel(logging.DEBUG)

            base_path = pathlib.Path(sys.executable).parent if getattr(sys, 'frozen', False) else pathlib.Path(__file__).parent
            log_dir = base_path / "logs"
            log_dir.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            cls._log_file_path = log_dir / f"ut_translation_installer-{timestamp}.log"

            file_handler = logging.FileHandler(cls._log_file_path, encoding="utf-8")
            stream_handler = logging.StreamHandler()

            file_handler.setLevel(logging.DEBUG)
            stream_handler.setLevel(logging.INFO)

            formatter = logging.Formatter(
                fmt="%(asctime)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )

            file_handler.setFormatter(formatter)
            stream_handler.setFormatter(formatter)

            cls._logger.addHandler(file_handler)
            cls._logger.addHandler(stream_handler)

        return cls._logger

    @classmethod
    def get_log_file_path(cls) -> pathlib.Path:
        if cls._log_file_path is None:
            raise RuntimeError("Logger has not been initialized")
        return cls._log_file_path