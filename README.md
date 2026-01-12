# NTFS Tool - Flash Copy Tool

A Python GUI application for efficiently copying files and directories with progress tracking and real-time logging.

## Features

- **Graphical User Interface**: Built with PySide6 for a user-friendly experience
- **Folder Selection**: Easy-to-use dialogs to select source and destination directories
- **Progress Tracking**: Real-time progress bar showing copy completion percentage
- **Live Logging**: Detailed log of all copied files and operations
- **Copy Management**: Start, cancel, and monitor file copy operations
- **Recursive Copying**: Automatically handles nested directory structures
- **Metadata Preservation**: Preserves file modification times and permissions during copy

## Requirements

- Python 3.14 or higher
- PySide6 >= 6.10.1

## Installation

1. Clone or download this repository
2. Install dependencies using uv:

```bash
uv sync
```

## Usage

Run the application:

```bash
uv run main.py
```

### How to Use

1. Click **"Select Source Folder"** to choose the directory containing files to copy
2. Click **"Select Destination Folder"** to choose where files will be copied to
3. Click **"Start Copy"** to begin the copy operation
4. Monitor progress through the progress bar and log output
5. Use **"Cancel"** to stop the operation at any time

## Project Structure

```
ntfs_tool/
├── main.py              # Application entry point
├── pyproject.toml       # Project configuration
├── README.md            # This file
├── gui/
│   └── main_window.py   # GUI components and window layout
└── logic/
    └── copy_worker.py   # File copy worker with threading support
```

## Technical Details

### Architecture

- **GUI Layer** (`gui/main_window.py`): Handles user interface using PySide6 Qt framework
- **Logic Layer** (`logic/copy_worker.py`): Manages file copying operations using threading

### Threading

The copy operation runs in a separate thread (`CopyWorker`) to prevent UI freezing during large file transfers. The worker communicates with the main GUI thread using Qt signals for progress updates and logging.

## Version

Current version: 0.1.0

## License

This project is licensed under the MIT License.

## Contributing

@sashakukhtyk
