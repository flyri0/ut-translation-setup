import io
import zipfile
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Signal, QObject, QThread, QFile, QTemporaryDir
from PySide6.QtWidgets import QWidget


class InstallFilesPage(QWidget):
    finished = Signal()

    def __init__(self):
        super().__init__()
        self._target_path: Optional[Path] = None
        self._is_demo: Optional[bool] = None
        self.temp_dir = QTemporaryDir()

    def set_target_path(self, target_path: Path):
        self._target_path = target_path

    def set_is_demo(self, is_demo: bool):
        self._is_demo = is_demo

    def _unzip(
            self,
            resource: str,
            destination: Path,
            folder_name: str
    ):
        file = QFile(resource)
        if not file.open(QFile.OpenModeFlag.ReadOnly):
            raise Exception(f"Failed to open resource {resource}")

        data = bytes(file.readAll().data())
        file.close()

        self.unzip_thread = QThread(self)
        self.unzip_worker = UnzipWorker()

        self.unzip_worker.moveToThread(self.unzip_thread)
        self.unzip_thread.started.connect(
            lambda: self.unzip_worker.run(data, destination, folder_name)
        )

        self.unzip_worker.finished.connect(self.unzip_thread.quit)
        self.unzip_worker.finished.connect(self.unzip_worker.deleteLater)
        self.unzip_thread.finished.connect(self.unzip_thread.deleteLater)

        self.unzip_thread.start()


class UnzipWorker(QObject):
    finished = Signal()
    error = Signal(Exception)
    total_files = Signal(int)
    progress = Signal(int, str)

    def run(self, data: bytes, destination: Path, folder_name: str):
        self._unzip(data, destination, folder_name)

    def _unzip(self, data: bytes, destination: Path, folder_name: str):
        dest_dir = Path(destination) / folder_name
        dest_dir.mkdir(parents=True, exist_ok=True)

        buffer = io.BytesIO(data)
        buffer.seek(0)

        try:
            with zipfile.ZipFile(buffer) as zf:
                infos = zf.infolist()
                self.total_files.emit(len(infos))

                count = 0
                for info in infos:
                    zf.extract(info, str(dest_dir.resolve()))
                    count += 1
                    self.progress.emit(count, info.filename)

            self.finished.emit()
        except Exception as e:
            self.error.emit(e)
            self.finished.emit()
            return None
