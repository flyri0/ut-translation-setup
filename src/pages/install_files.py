import io
import platform
import shutil
import stat
import zipfile
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Signal, QObject, QThread, QFile, QTemporaryDir, \
    Qt, QProcess, QTimer
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

    def showEvent(self, event) -> None:
        super().showEvent(event)

        self._unzip_translation_files()

    def _ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 0, 50, 0)

        self.status_label = QLabel()
        self.status_label.setText(self.tr("Extracting Files..."))
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.progress_bar = QProgressBar()
        self.progress_bar.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.progress_bar.setRange(0, 0)

        self.log_widget = _LogWidget()

        layout.addStretch()
        layout.addWidget(self.status_label)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.log_widget)
        layout.addStretch()

    def _unzip_translation_files(self):
        temp_dir_path = Path(self.temp_dir.path())
        translation_files_resource = ":translation_files"

        self._unzip(
            translation_files_resource,
            temp_dir_path,
            "translation_files",
            on_finished=self._unzip_pck_explorer,
        )

    def _unzip_pck_explorer(self):
        system = platform.system()
        temp_dir_path = Path(self.temp_dir.path())
        pck_explorer_bin: str

        if system == "Windows":
            pck_explorer_bin = ":win_pck_explorer"
        else:
            pck_explorer_bin = ":linux_pck_explorer"

        self._clear_feedback()
        self._unzip(
            pck_explorer_bin,
            temp_dir_path,
            "pck_explorer",
            on_finished=self._install_files,
        )

    def _install_files(self):
        self.status_label.setText(self.tr("Installing translation files..."))
        self.progress_bar.setRange(0, 0)

        system = platform.system()
        temp_dir_path = Path(self.temp_dir.path())
        base_files_path = temp_dir_path / "translation_files"
        files_path: Path
        pck_explorer_bin = temp_dir_path / "pck_explorer"

        if self._is_demo:
            files_path = base_files_path / "demo"
        else:
            files_path = base_files_path / "full"

        if system == "Windows":
            pck_explorer_bin = (pck_explorer_bin
                                / "GodotPCKExplorer.Console.exe")
        else:
            pck_explorer_bin = pck_explorer_bin / "GodotPCKExplorer.Console"
            mode = pck_explorer_bin.stat().st_mode
            if not (mode & stat.S_IXUSR):
                pck_explorer_bin.chmod(mode | stat.S_IXUSR)

        self.process = QProcess()
        self.timer = QTimer()
        self.timer.timeout.connect(self._log_output)
        self.timer.start(1000)
        self.process.finished.connect(self._on_install_finished)
        self.process.setProcessChannelMode(
            QProcess.ProcessChannelMode.MergedChannels
        )

        self.process.start(
            str(pck_explorer_bin.absolute().resolve()),
            [
                "-pc",
                str(self._target_path.absolute().resolve()),
                str(files_path.absolute().resolve()),
                str(Path(self._target_path.parent / "ModifiedPCK.pck")
                    .absolute().resolve()),
                "2.2.4.1"
            ]
        )

    def _log_output(self):
        byte_array = self.process.readLine()
        text = byte_array.data().decode(errors="replace")
        system = platform.system()

        if system == "Windows":
            self.log_widget.setVisible(False)
            return

        self.log_widget.append(text)

    def _on_install_finished(self):
        src = Path(self._target_path)
        backup = src.with_name(src.name + ".bak")
        modified = Path(src.parent) / "ModifiedPCK.pck"

        if src.exists():
            shutil.move(str(src), str(backup))

        shutil.move(str(modified), str(src))

        self.finished.emit()

    def _clear_feedback(self):
        self._total_files = 0
        self.progress_bar.setValue(0)
        self.progress_bar.setRange(0, 0)
        self.status_label.setText(self.tr("Extraction Complete!"))
        self.log_widget.clear()

    def set_target_path(self, target_path: Path):
        self._target_path = target_path

    def set_is_demo(self, is_demo: bool):
        self._is_demo = is_demo

    def _on_total_files(self, total_files: int):
        self.progress_bar.setRange(0, total_files)
        self._total_files = total_files

    def _on_progress(self, count: int, name: str):
        self.status_label.setText(
            self.tr("Extracting ")
            + str(count)
            + self.tr(" of ")
            + str(self._total_files)
        )
        self.progress_bar.setValue(count)
        self.log_widget.append_message(name)

    def _unzip(
            self,
            resource: str,
            destination: Path,
            folder_name: str,
            on_finished,
    ):
        file = QFile(resource)
        if not file.open(QFile.OpenModeFlag.ReadOnly):
            raise Exception(f"Failed to open resource {resource}")

        data = bytes(file.readAll().data())
        file.close()

        unzip_thread = QThread(self)
        unzip_worker = _UnzipWorker()

        unzip_worker.moveToThread(unzip_thread)
        unzip_thread.started.connect(
            lambda: unzip_worker.run(data, destination, folder_name)
        )

        unzip_worker.total_files.connect(self._on_total_files)
        unzip_worker.progress.connect(self._on_progress)
        if on_finished:
            unzip_worker.finished.connect(on_finished)

        unzip_worker.finished.connect(unzip_thread.quit)
        unzip_worker.finished.connect(unzip_worker.deleteLater)
        unzip_thread.finished.connect(unzip_thread.deleteLater)

        unzip_thread.start()


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
            return None


class _LogWidget(QTextEdit):
    def __init__(self):
        super().__init__()

        self.setReadOnly(True)
        self.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.viewport().setCursor(Qt.CursorShape.ArrowCursor)
        self.document().setMaximumBlockCount(100)
        self.horizontalScrollBar().setVisible(False)
        self.setStyleSheet("""
            QTextEdit {
                font-family: sans-serif;
                font-size: 10pt;
            }
        """)

    def append_message(self, message: str):
        self.append(message)

        scrollbar = self.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
