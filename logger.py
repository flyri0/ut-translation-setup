from datetime import datetime
import logging
import pathlib


class AppLogger:
    _logger: logging.Logger = None

    @classmethod
    def get_logger(cls) -> logging.Logger:
        if cls._logger is None:
            cls._logger = logging.getLogger("AppLogger")
            cls._logger.setLevel(logging.DEBUG)

            log_dir = pathlib.Path(__file__).parent / "logs"
            log_dir.mkdir(exist_ok=True)

            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            log_file_path = log_dir / f"{timestamp}.log"

            file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
            stream_handler = logging.StreamHandler()

            file_handler.setLevel(logging.DEBUG)
            stream_handler.setLevel(logging.INFO)

            formatter = logging.Formatter(
                fmt="%(asctime)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )

            file_handler.setFormatter(formatter)
            stream_handler.setFormatter(formatter)

            cls._logger.addHandler(file_handler)
            cls._logger.addHandler(stream_handler)

        return cls._logger
