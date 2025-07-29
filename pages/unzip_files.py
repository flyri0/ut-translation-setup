import gettext
import io
import zipfile
from pathlib import Path

import qtawesome
from PySide6.QtCore import Qt, QObject, Signal, QFile, QThread, Slot
from PySide6.QtWidgets import QVBoxLayout, QLabel, QProgressBar, QPlainTextEdit, QSizePolicy, QPushButton

from pages.base import BasePage

_ = gettext.gettext

LOG_PREFIX = "UnzipFilesPage:"

class UnzipFilesPage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.controller.logger.debug(f"{LOG_PREFIX} Initialized page")
        self._build_ui()
        self.controller.logger.debug(f"{LOG_PREFIX} UI built")

    def showEvent(self, event):
        super().showEvent(event)
        self.controller.logger.debug(f"{LOG_PREFIX} showEvent: hiding back button and disabling next")
        self.controller.back_button.setVisible(False)
        self.controller.next_button.setEnabled(False)

    def _build_ui(self):
        self.controller.logger.debug(f"{LOG_PREFIX} Building UI components")
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.progressbar = QProgressBar()
        self.progressbar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progressbar.setTextVisible(False)

        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.log_frame = LogFrame()
        self.log_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        self.unzip_button = QPushButton()
        self.unzip_button.setText(_("Descompactar arquivos"))
        self.unzip_button.setIcon(qtawesome.icon("fa6s.file-zipper"))
        self.unzip_button.setDefault(True)
        self.unzip_button.clicked.connect(self._unzip_files)

        layout.addWidget(self.status_label)
        layout.addWidget(self.progressbar)
        layout.addWidget(self.log_frame)
        layout.addWidget(self.unzip_button)
        self.controller.logger.debug(f"{LOG_PREFIX} UI layout complete")

    def _unzip_files(self):
        self.controller.logger.info(f"{LOG_PREFIX} Starting unzip worker thread")
        self.unzip_thread = QThread(self)
        self.unzip_worker = UnzipWorker(
            QFile(":/assets/translation_files.zip"),
            self.controller.state.temp_dir
        )
        self.unzip_worker.moveToThread(self.unzip_thread)

        self.unzip_thread.started.connect(self.unzip_worker.run)

        self.unzip_worker.total_files.connect(self._on_total_files)
        self.unzip_worker.extracted_file.connect(self._on_extracted)
        self.unzip_worker.finished.connect(self._on_unzip_finished)

        self.unzip_worker.finished.connect(self.unzip_thread.quit)
        self.unzip_worker.finished.connect(self.unzip_worker.deleteLater)
        self.unzip_worker.finished.connect(self.unzip_thread.deleteLater)

        self.unzip_thread.start()

    def _on_total_files(self, total):
        self.controller.logger.debug(f"{LOG_PREFIX} Total files to extract: {total}")
        self.status_label.setText(_("Descompactando 0 de {total} arquivos...").format(total=total))
        self.progressbar.setRange(0, total)
        self.progressbar.setValue(0)

    def _on_extracted(self, count, file_name):
        self.controller.logger.debug(f"{LOG_PREFIX} Extracted {file_name} ({count}/{self.progressbar.maximum()})")
        self.progressbar.setValue(count)
        self.log_frame.append_message(file_name)
        self.status_label.setText(_("Descompactando {count}/{total}").format(
            count=count,
            total=self.progressbar.maximum()
        ))

    def _on_unzip_finished(self, success, message):
        if success:
            self.controller.logger.info(f"{LOG_PREFIX} Unzip completed, files extracted to {message}")
            self.status_label.setText(_("Descompressão concluída!"))
            self.controller.next_button.setEnabled(True)
            self.unzip_button.setEnabled(False)
        else:
            self.controller.logger.critical(f"{LOG_PREFIX} Unzip failed: {message}")
            raise RuntimeError(message)

class LogFrame(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setReadOnly(True)
        self.viewport().setCursor(Qt.CursorShape.ArrowCursor)
        self.controller_logger = None

    def append_message(self, message: str):
        self.appendPlainText(message)

        scrollbar = self.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

class UnzipWorker(QObject):
    total_files = Signal(int)
    extracted_file = Signal(int, str)
    finished = Signal(bool, str)

    def __init__(self, file: QFile, dest_dir: Path):
        super().__init__()
        self.file = file
        self.dest_dir = dest_dir.absolute().resolve()

    @Slot()
    def run(self):
        try:
            if not self.file.open(QFile.OpenModeFlag.ReadOnly):
                raise IOError(f"Cannot open resource {str(self.file)}")

            data = self.file.readAll().data()
            buffer = io.BytesIO(data)

            zf = zipfile.ZipFile(buffer)
            infos = zf.infolist()
            total = len(infos)
            self.total_files.emit(total)
            count = 0

            for info in infos:
                zf.extract(info, self.dest_dir)
                count += 1
                self.extracted_file.emit(count, str(info.filename))
            zf.close()
            self.finished.emit(True, str(self.dest_dir))
        except Exception as error:
            self.finished.emit(False, str(error))
        finally:
            self.file.close()
