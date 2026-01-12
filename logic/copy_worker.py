"""
File copy worker module for handling file operations with progress tracking.
Provides a worker class that can be run in a separate thread for non-blocking file copy operations.
"""
import shutil
from pathlib import Path
from PySide6.QtCore import QObject, Signal


class CopyWorker(QObject):
    """
    A worker class for copying files recursively with progress tracking.
    Emits signals for progress updates, log messages, completion, and errors.
    Designed to be run in a QThread for non-blocking UI operations.
    """
    progress = Signal(int)
    log = Signal(str)
    finished = Signal()
    error = Signal(str)

    def __init__(self, source: Path, destination: Path):
        super().__init__()
        self.source = source
        self.destination = destination
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def run(self):
        try:
            files = [p for p in self.source.rglob("*") if p.is_file()]
            total = len(files)

            if total == 0:
                self.log.emit("No files to copy.")
                self.finished.emit()
                return

            copied = 0

            for src_file in files:
                if self._cancelled:
                    self.log.emit("Copy cancelled.")
                    return

                rel_path = src_file.relative_to(self.source)
                dst_file = self.destination / rel_path

                dst_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_file, dst_file)

                copied += 1
                percent = int((copied / total) * 100)

                self.progress.emit(percent)
                self.log.emit(f"Copied: {rel_path}")

            self.finished.emit()

        except Exception as e:
            self.error.emit(str(e))
