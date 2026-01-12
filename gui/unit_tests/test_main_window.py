import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, call
import tempfile
import shutil

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt, QThread

from ..main_window import MainWindow


class TestMainWindow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Create QApplication instance for all tests."""
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()

    def setUp(self):
        """Set up MainWindow instance before each test."""
        self.window = MainWindow()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up after each test."""
        self.window.close()
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)

    def test_window_initialization(self):
        """Test that MainWindow initializes with correct properties."""
        self.assertEqual(self.window.windowTitle(), "Flash Copy Tool")
        self.assertEqual(self.window.width(), 650)
        self.assertEqual(self.window.height(), 450)

    def test_initial_labels(self):
        """Test that initial labels are set correctly."""
        self.assertEqual(self.window.src_label.text(), "Source: not selected")
        self.assertEqual(self.window.dst_label.text(), "Destination: not selected")

    def test_start_button_initially_disabled(self):
        """Test that Start Copy button is disabled initially."""
        self.assertFalse(self.window.start_btn.isEnabled())

    def test_cancel_button_initially_disabled(self):
        """Test that Cancel button is disabled initially."""
        self.assertFalse(self.window.cancel_btn.isEnabled())

    def test_progress_bar_initial_value(self):
        """Test that progress bar starts at 0."""
        self.assertEqual(self.window.progress.value(), 0)

    def test_log_is_readonly(self):
        """Test that log text edit is read-only."""
        self.assertTrue(self.window.log.isReadOnly())

    def test_initial_paths_are_none(self):
        """Test that source and destination paths are initially None."""
        self.assertIsNone(self.window.source_path)
        self.assertIsNone(self.window.dest_path)

    def test_initial_thread_and_worker_are_none(self):
        """Test that thread and worker are initially None."""
        self.assertIsNone(self.window.thread)
        self.assertIsNone(self.window.worker)

    @patch('gui.main_window.QFileDialog.getExistingDirectory')
    def test_select_source(self, mock_dialog):
        """Test selecting source folder."""
        source_path = str(Path(self.temp_dir) / "source")
        Path(source_path).mkdir()
        mock_dialog.return_value = source_path

        self.window.select_source()

        self.assertEqual(self.window.source_path, Path(source_path))
        self.assertIn(source_path, self.window.src_label.text())

    @patch('gui.main_window.QFileDialog.getExistingDirectory')
    def test_select_source_adds_log_message(self, mock_dialog):
        """Test that selecting source adds log message."""
        source_path = str(Path(self.temp_dir) / "source")
        Path(source_path).mkdir()
        mock_dialog.return_value = source_path

        self.window.select_source()

        self.assertIn(f"Source selected: {source_path}", self.window.log.toPlainText())

    @patch('gui.main_window.QFileDialog.getExistingDirectory')
    def test_select_source_empty_dialog(self, mock_dialog):
        """Test that cancelling source selection doesn't change path."""
        mock_dialog.return_value = ""

        self.window.select_source()

        self.assertIsNone(self.window.source_path)

    @patch('gui.main_window.QFileDialog.getExistingDirectory')
    def test_select_destination(self, mock_dialog):
        """Test selecting destination folder."""
        dest_path = str(Path(self.temp_dir) / "destination")
        Path(dest_path).mkdir()
        mock_dialog.return_value = dest_path

        self.window.select_destination()

        self.assertEqual(self.window.dest_path, Path(dest_path))
        self.assertIn(dest_path, self.window.dst_label.text())

    @patch('gui.main_window.QFileDialog.getExistingDirectory')
    def test_select_destination_adds_log_message(self, mock_dialog):
        """Test that selecting destination adds log message."""
        dest_path = str(Path(self.temp_dir) / "destination")
        Path(dest_path).mkdir()
        mock_dialog.return_value = dest_path

        self.window.select_destination()

        self.assertIn(f"Destination selected: {dest_path}", self.window.log.toPlainText())

    def test_check_ready_with_no_paths(self):
        """Test that Start button is disabled with no paths."""
        self.window.check_ready()
        self.assertFalse(self.window.start_btn.isEnabled())

    def test_check_ready_with_source_only(self):
        """Test that Start button is disabled with only source."""
        self.window.source_path = Path(self.temp_dir)
        self.window.check_ready()
        self.assertFalse(self.window.start_btn.isEnabled())

    def test_check_ready_with_destination_only(self):
        """Test that Start button is disabled with only destination."""
        self.window.dest_path = Path(self.temp_dir)
        self.window.check_ready()
        self.assertFalse(self.window.start_btn.isEnabled())

    def test_check_ready_with_both_paths(self):
        """Test that Start button is enabled with both paths."""
        self.window.source_path = Path(self.temp_dir)
        self.window.dest_path = Path(self.temp_dir)
        self.window.check_ready()
        self.assertTrue(self.window.start_btn.isEnabled())

    @patch('gui.main_window.QThread')
    @patch('gui.main_window.CopyWorker')
    def test_start_copy_creates_thread_and_worker(self, mock_worker_class, mock_thread_class):
        """Test that start_copy creates thread and worker."""
        mock_thread = MagicMock()
        mock_worker = MagicMock()
        mock_thread_class.return_value = mock_thread
        mock_worker_class.return_value = mock_worker

        self.window.source_path = Path(self.temp_dir)
        self.window.dest_path = Path(self.temp_dir)

        self.window.start_copy()

        self.assertIsNotNone(self.window.thread)
        self.assertIsNotNone(self.window.worker)
        mock_worker_class.assert_called_once_with(self.window.source_path, self.window.dest_path)

    @patch('gui.main_window.QThread')
    @patch('gui.main_window.CopyWorker')
    def test_start_copy_disables_start_button(self, mock_worker_class, mock_thread_class):
        """Test that start_copy disables Start button."""
        mock_thread = MagicMock()
        mock_worker = MagicMock()
        mock_thread_class.return_value = mock_thread
        mock_worker_class.return_value = mock_worker

        self.window.source_path = Path(self.temp_dir)
        self.window.dest_path = Path(self.temp_dir)
        self.window.start_btn.setEnabled(True)

        self.window.start_copy()

        self.assertFalse(self.window.start_btn.isEnabled())

    @patch('gui.main_window.QThread')
    @patch('gui.main_window.CopyWorker')
    def test_start_copy_enables_cancel_button(self, mock_worker_class, mock_thread_class):
        """Test that start_copy enables Cancel button."""
        mock_thread = MagicMock()
        mock_worker = MagicMock()
        mock_thread_class.return_value = mock_thread
        mock_worker_class.return_value = mock_worker

        self.window.source_path = Path(self.temp_dir)
        self.window.dest_path = Path(self.temp_dir)

        self.window.start_copy()

        self.assertTrue(self.window.cancel_btn.isEnabled())

    @patch('gui.main_window.QThread')
    @patch('gui.main_window.CopyWorker')
    def test_start_copy_resets_progress(self, mock_worker_class, mock_thread_class):
        """Test that start_copy resets progress bar."""
        mock_thread = MagicMock()
        mock_worker = MagicMock()
        mock_thread_class.return_value = mock_thread
        mock_worker_class.return_value = mock_worker

        self.window.source_path = Path(self.temp_dir)
        self.window.dest_path = Path(self.temp_dir)
        self.window.progress.setValue(50)

        self.window.start_copy()

        self.assertEqual(self.window.progress.value(), 0)

    @patch('gui.main_window.QThread')
    @patch('gui.main_window.CopyWorker')
    def test_start_copy_adds_log_message(self, mock_worker_class, mock_thread_class):
        """Test that start_copy adds log message."""
        mock_thread = MagicMock()
        mock_worker = MagicMock()
        mock_thread_class.return_value = mock_thread
        mock_worker_class.return_value = mock_worker

        self.window.source_path = Path(self.temp_dir)
        self.window.dest_path = Path(self.temp_dir)

        self.window.start_copy()

        self.assertIn("Starting copy...", self.window.log.toPlainText())

    @patch('gui.main_window.QThread')
    @patch('gui.main_window.CopyWorker')
    def test_start_copy_connects_signals(self, mock_worker_class, mock_thread_class):
        """Test that start_copy connects signals properly."""
        mock_thread = MagicMock()
        mock_worker = MagicMock()
        mock_thread_class.return_value = mock_thread
        mock_worker_class.return_value = mock_worker

        self.window.source_path = Path(self.temp_dir)
        self.window.dest_path = Path(self.temp_dir)

        self.window.start_copy()

        # Verify signal connections
        mock_thread.started.connect.assert_called()
        mock_worker.progress.connect.assert_called()
        mock_worker.log.connect.assert_called()
        mock_worker.finished.connect.assert_called()
        mock_worker.error.connect.assert_called()

    @patch('gui.main_window.QThread')
    @patch('gui.main_window.CopyWorker')
    def test_start_copy_starts_thread(self, mock_worker_class, mock_thread_class):
        """Test that start_copy starts the thread."""
        mock_thread = MagicMock()
        mock_worker = MagicMock()
        mock_thread_class.return_value = mock_thread
        mock_worker_class.return_value = mock_worker

        self.window.source_path = Path(self.temp_dir)
        self.window.dest_path = Path(self.temp_dir)

        self.window.start_copy()

        mock_thread.start.assert_called_once()

    def test_start_copy_returns_early_if_no_paths(self):
        """Test that start_copy returns early if paths are not set."""
        self.window.source_path = None
        self.window.dest_path = None

        # Should not raise an error
        self.window.start_copy()

    @patch('gui.main_window.CopyWorker')
    def test_cancel_copy(self, mock_worker_class):
        """Test that cancel_copy calls worker.cancel()."""
        mock_worker = MagicMock()
        self.window.worker = mock_worker

        self.window.cancel_copy()

        mock_worker.cancel.assert_called_once()

    def test_cancel_copy_adds_log_message(self):
        """Test that cancel_copy adds log message."""
        mock_worker = MagicMock()
        self.window.worker = mock_worker

        self.window.cancel_copy()

        self.assertIn("Cancelling...", self.window.log.toPlainText())

    def test_copy_finished_sets_progress_to_100(self):
        """Test that copy_finished sets progress to 100%."""
        self.window.progress.setValue(50)
        self.window.copy_finished()
        self.assertEqual(self.window.progress.value(), 100)

    def test_copy_finished_adds_log_message(self):
        """Test that copy_finished adds log message."""
        self.window.copy_finished()
        self.assertIn("Copy completed successfully.", self.window.log.toPlainText())

    def test_copy_finished_enables_start_button(self):
        """Test that copy_finished enables Start button."""
        self.window.start_btn.setEnabled(False)
        self.window.copy_finished()
        self.assertTrue(self.window.start_btn.isEnabled())

    def test_copy_finished_disables_cancel_button(self):
        """Test that copy_finished disables Cancel button."""
        self.window.cancel_btn.setEnabled(True)
        self.window.copy_finished()
        self.assertFalse(self.window.cancel_btn.isEnabled())

    @patch('gui.main_window.QMessageBox.critical')
    def test_copy_error_shows_message_box(self, mock_msgbox):
        """Test that copy_error shows error message box."""
        error_msg = "Test error message"
        self.window.copy_error(error_msg)
        mock_msgbox.assert_called_once_with(self.window, "Copy Error", error_msg)

    @patch('gui.main_window.QFileDialog.getExistingDirectory')
    def test_select_source_enables_start_button_when_dest_set(self, mock_dialog):
        """Test that selecting source enables Start button if destination is set."""
        source_path = str(Path(self.temp_dir) / "source")
        Path(source_path).mkdir()
        mock_dialog.return_value = source_path

        self.window.dest_path = Path(self.temp_dir)
        self.window.select_source()

        self.assertTrue(self.window.start_btn.isEnabled())

    @patch('gui.main_window.QFileDialog.getExistingDirectory')
    def test_select_destination_enables_start_button_when_src_set(self, mock_dialog):
        """Test that selecting destination enables Start button if source is set."""
        dest_path = str(Path(self.temp_dir) / "destination")
        Path(dest_path).mkdir()
        mock_dialog.return_value = dest_path

        self.window.source_path = Path(self.temp_dir)
        self.window.select_destination()

        self.assertTrue(self.window.start_btn.isEnabled())


if __name__ == "__main__":
    unittest.main()
