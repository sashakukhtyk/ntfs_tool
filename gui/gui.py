import sys
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QPushButton,
    QLabel,
    QProgressBar,
    QTextEdit,
    QFileDialog,
    QVBoxLayout,
    QHBoxLayout,
)
from PySide6.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Flash Copy Tool")
        self.resize(600, 400)

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)

        # Source selector
        self.src_label = QLabel("Source: not selected")
        src_btn = QPushButton("Select Source Folder")
        src_btn.clicked.connect(self.select_source)

        # Destination selector
        self.dst_label = QLabel("Destination: not selected")
        dst_btn = QPushButton("Select Destination Folder")
        dst_btn.clicked.connect(self.select_destination)

        # Start button
        self.start_btn = QPushButton("Start Copy")
        self.start_btn.setEnabled(False)
        self.start_btn.clicked.connect(self.start_copy)

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setValue(0)

        # Log output
        self.log = QTextEdit()
        self.log.setReadOnly(True)

        # Layouts
        layout.addWidget(self.src_label)
        layout.addWidget(src_btn)
        layout.addWidget(self.dst_label)
        layout.addWidget(dst_btn)
        layout.addWidget(self.start_btn)
        layout.addWidget(self.progress)
        layout.addWidget(self.log)

        self.source_path = None
        self.dest_path = None

    def select_source(self):
        path = QFileDialog.getExistingDirectory(
            self, "Select Source Folder"
        )
        if path:
            self.source_path = path
            self.src_label.setText(f"Source: {path}")
            self.log.append(f"Source selected: {path}")
            self.check_ready()

    def select_destination(self):
        path = QFileDialog.getExistingDirectory(
            self, "Select Destination Folder"
        )
        if path:
            self.dest_path = path
            self.dst_label.setText(f"Destination: {path}")
            self.log.append(f"Destination selected: {path}")
            self.check_ready()

    def check_ready(self):
        self.start_btn.setEnabled(
            self.source_path is not None and self.dest_path is not None
        )

    def start_copy(self):
        # Placeholder for now
        self.log.append("Start copy clicked (logic not implemented yet)")
        self.progress.setValue(0)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
