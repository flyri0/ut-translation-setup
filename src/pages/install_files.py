import io
import zipfile
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Signal, QObject, QThread, QFile, QTemporaryDir, Qt
from PySide6.QtWidgets import QWidget, QTextEdit, QVBoxLayout, QProgressBar, \
    QLabel


class InstallFilesPage(QWidget):
    finished = Signal()

    def __init__(self):
        super().__init__()
        self._target_path: Optional[Path] = None
        self._is_demo: Optional[bool] = None
        self._total_files = 0
        self.temp_dir = QTemporaryDir()
        self._ui()

    def _ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(100, 0, 100, 0)

        self.status_label = QLabel()
        self.status_label.setText(self.tr("Extracting Files..."))
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.progress_bar = QProgressBar()

        self.log_widget = _LogWidget()

        layout.addStretch()
        layout.addWidget(self.status_label)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.log_widget)
        layout.addStretch()

    def set_target_path(self, target_path: Path):
        self._target_path = target_path

    def set_is_demo(self, is_demo: bool):
        self._is_demo = is_demo

    def _on_total_files(self, total_files: int):
        self.progress_bar.setRange(0, total_files)
        self._total_files = total_files

    def _on_progress(self, count: int, name: str):
        self.status_label.setText(self.tr(
            f"Extracting {count} of {self._total_files}"
        ))
        self.progress_bar.setValue(count)
        self.log_widget.append_message(name)

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
        self.unzip_worker = _UnzipWorker()

        self.unzip_worker.moveToThread(self.unzip_thread)
        self.unzip_thread.started.connect(
            lambda: self.unzip_worker.run(data, destination, folder_name)
        )

        self.unzip_worker.total_files.connect(self._on_total_files)
        self.unzip_worker.progress.connect(self._on_progress)

        self.unzip_worker.finished.connect(self.unzip_thread.quit)
        self.unzip_worker.finished.connect(self.unzip_worker.deleteLater)
        self.unzip_thread.finished.connect(self.unzip_thread.deleteLater)

        self.unzip_thread.start()


class _UnzipWorker(QObject):
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


class _LogWidget(QTextEdit):
    def __init__(self):
        super().__init__()

        self.setReadOnly(True)
        self.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.viewport().setCursor(Qt.CursorShape.ArrowCursor)

    def append_message(self, message: str):
        self.append(message)

        scrollbar = self.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
