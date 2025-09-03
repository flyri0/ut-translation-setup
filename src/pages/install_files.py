import io
import zipfile
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QObject, Signal, QFile, Slot, QThread
from PySide6.QtWidgets import QPushButton

from src.pages.base import BasePage


class InstallFilesPage(BasePage):
    def _build_ui(self):
        self.btn = QPushButton(self)
        self.btn.setText("Install")
        self.btn.clicked.connect(self._install_files)

    def _install_files(self):
        self.install_thread = QThread(self)
        self.install_worker = InstallWorker(
            temp_dir=self.controller.state.temp_dir,
            pck_path=self.controller.state.pck_path,
            translation_files_zip=QFile(":translation_files_zip"),
            pck_explorer_bin=QFile(":pck_explorer_win")
        )

        self.install_worker.moveToThread(self.install_thread)
        self.install_thread.started.connect(self.install_worker.run)
        self.install_worker.finished.connect(self._on_finish)

        self.install_worker.finished.connect(self.install_thread.quit)
        self.install_worker.finished.connect(self.install_worker.deleteLater)
        self.install_thread.finished.connect(self.install_thread.deleteLater)

        self.install_thread.start()

    def _on_finish(self):
        print(str(self.controller.state.temp_dir))


class InstallWorker(QObject):
    error = Signal(Exception)
    finished = Signal()
    total_files = Signal(int)
    progress = Signal(int, str)

    def __init__(
            self,
            temp_dir: Path,
            pck_path: Path,
            translation_files_zip: QFile,
            pck_explorer_bin: QFile
    ):
        super().__init__()
        self.temp_dir = Path(temp_dir)
        self.pck_path = Path(pck_path)
        self.translation_files_zip = translation_files_zip
        self.pck_explorer_bin = pck_explorer_bin

    @Slot()
    def run(self):
        self.unzip(self.translation_files_zip, self.temp_dir)
        self.unzip(self.pck_explorer_bin, self.temp_dir)
        self.finished.emit()

    def unzip(self, file: QFile, destination: Path) -> Optional[Path]:
        try:
            if not file.open(QFile.OpenModeFlag.ReadOnly):
                raise RuntimeError(f"Cannot open resource: {str(file)}")
        except RuntimeError as error:
            self.error.emit(error)
            return None

        dest_dir = Path(destination)
        dest_dir.mkdir(parents=True, exist_ok=True)
        data = file.readAll().data()
        buffer = io.BytesIO(data)

        try:
            with zipfile.ZipFile(buffer) as zf:
                infos = zf.infolist()
                self.total_files.emit(len(infos))
                count = 0
                for info in infos:
                    zf.extract(info, str(dest_dir))
                    count += 1
                    self.progress.emit(count, info.filename)
                return dest_dir
        except Exception as error:
            self.error.emit(error)
            return None
        finally:
            file.close()
