from pathlib import Path

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QPushButton,
    QLabel,
    QProgressBar,
    QTextEdit,
    QFileDialog,
    QVBoxLayout,
    QMessageBox,
)
from PySide6.QtCore import QThread

from logic.copy_worker import CopyWorker


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Flash Copy Tool")
        self.resize(650, 450)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        self.src_label = QLabel("Source: not selected")
        self.dst_label = QLabel("Destination: not selected")

        src_btn = QPushButton("Select Source Folder")
        dst_btn = QPushButton("Select Destination Folder")

        src_btn.clicked.connect(self.select_source)
        dst_btn.clicked.connect(self.select_destination)

        self.start_btn = QPushButton("Start Copy")
        self.start_btn.setEnabled(False)
        self.start_btn.clicked.connect(self.start_copy)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self.cancel_copy)

        self.progress = QProgressBar()
        self.progress.setValue(0)

        self.log = QTextEdit()
        self.log.setReadOnly(True)

        layout.addWidget(self.src_label)
        layout.addWidget(src_btn)
        layout.addWidget(self.dst_label)
        layout.addWidget(dst_btn)
        layout.addWidget(self.start_btn)
        layout.addWidget(self.cancel_btn)
        layout.addWidget(self.progress)
        layout.addWidget(self.log)

        self.source_path: Path | None = None
        self.dest_path: Path | None = None

        self.thread = None
        self.worker = None

    # --------------------
    # UI actions
    # --------------------
    def select_source(self):
        path = QFileDialog.getExistingDirectory(self, "Select Source Folder")
        if path:
            self.source_path = Path(path)
            self.src_label.setText(f"Source: {path}")
            self.log.append(f"Source selected: {path}")
            self.check_ready()

    def select_destination(self):
        path = QFileDialog.getExistingDirectory(self, "Select Destination Folder")
        if path:
            self.dest_path = Path(path)
            self.dst_label.setText(f"Destination: {path}")
            self.log.append(f"Destination selected: {path}")
            self.check_ready()

    def check_ready(self):
        self.start_btn.setEnabled(
            self.source_path is not None and self.dest_path is not None
        )

    def start_copy(self):
        if not self.source_path or not self.dest_path:
            return

        self.progress.setValue(0)
        self.log.append("Starting copy...")

        self.start_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)

        self.thread = QThread()
        self.worker = CopyWorker(self.source_path, self.dest_path)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.progress.setValue)
        self.worker.log.connect(self.log.append)
        self.worker.finished.connect(self.copy_finished)
        self.worker.error.connect(self.copy_error)

        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def cancel_copy(self):
        if self.worker:
            self.worker.cancel()
            self.log.append("Cancelling...")

    def copy_finished(self):
        self.progress.setValue(100)
        self.log.append("Copy completed successfully.")
        self.start_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)

    def copy_error(self, message):
        QMessageBox.critical(self, "Copy Error", message)
        self.log.append(f"ERROR: {message}")
        self.start_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
