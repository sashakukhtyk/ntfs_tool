import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from PySide6.QtCore import QObject
import tempfile
import shutil

from ..copy_worker import CopyWorker


class TestCopyWorker(unittest.TestCase):
    def setUp(self):
        """Set up temporary directories for testing."""
        self.temp_dir = tempfile.mkdtemp()
        self.source_dir = Path(self.temp_dir) / "source"
        self.dest_dir = Path(self.temp_dir) / "destination"
        self.source_dir.mkdir()

    def tearDown(self):
        """Clean up temporary directories after testing."""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)

    def test_init(self):
        """Test CopyWorker initialization."""
        worker = CopyWorker(self.source_dir, self.dest_dir)
        self.assertEqual(worker.source, self.source_dir)
        self.assertEqual(worker.destination, self.dest_dir)
        self.assertFalse(worker._cancelled)

    def test_cancel(self):
        """Test that cancel method sets _cancelled flag to True."""
        worker = CopyWorker(self.source_dir, self.dest_dir)
        self.assertFalse(worker._cancelled)
        worker.cancel()
        self.assertTrue(worker._cancelled)

    def test_signals_exist(self):
        """Test that all required signals are defined."""
        worker = CopyWorker(self.source_dir, self.dest_dir)
        self.assertTrue(hasattr(worker, 'progress'))
        self.assertTrue(hasattr(worker, 'log'))
        self.assertTrue(hasattr(worker, 'finished'))
        self.assertTrue(hasattr(worker, 'error'))

    def test_run_no_files(self):
        """Test run method when source directory is empty."""
        worker = CopyWorker(self.source_dir, self.dest_dir)
        
        # Mock the signals
        worker.log = Mock()
        worker.finished = Mock()
        
        worker.run()
        
        worker.log.emit.assert_called_once_with("No files to copy.")
        worker.finished.emit.assert_called_once()

    def test_run_single_file(self):
        """Test copying a single file."""
        # Create a test file
        test_file = self.source_dir / "test.txt"
        test_file.write_text("test content")
        
        worker = CopyWorker(self.source_dir, self.dest_dir)
        
        # Mock the signals
        worker.log = Mock()
        worker.progress = Mock()
        worker.finished = Mock()
        
        worker.run()
        
        # Verify file was copied
        copied_file = self.dest_dir / "test.txt"
        self.assertTrue(copied_file.exists())
        self.assertEqual(copied_file.read_text(), "test content")
        
        # Verify signals were emitted
        worker.progress.emit.assert_called_with(100)
        worker.finished.emit.assert_called_once()

    def test_run_multiple_files(self):
        """Test copying multiple files."""
        # Create test files
        file1 = self.source_dir / "file1.txt"
        file2 = self.source_dir / "file2.txt"
        file1.write_text("content1")
        file2.write_text("content2")
        
        worker = CopyWorker(self.source_dir, self.dest_dir)
        
        # Mock the signals
        worker.log = Mock()
        worker.progress = Mock()
        worker.finished = Mock()
        
        worker.run()
        
        # Verify files were copied
        self.assertTrue((self.dest_dir / "file1.txt").exists())
        self.assertTrue((self.dest_dir / "file2.txt").exists())
        
        # Verify progress was updated correctly
        self.assertEqual(worker.progress.emit.call_count, 2)
        
        # Verify log messages
        self.assertEqual(worker.log.emit.call_count, 2)
        
        worker.finished.emit.assert_called_once()

    def test_run_nested_directories(self):
        """Test copying files from nested directories."""
        # Create nested directory structure
        nested_dir = self.source_dir / "subdir" / "nested"
        nested_dir.mkdir(parents=True)
        
        nested_file = nested_dir / "nested.txt"
        nested_file.write_text("nested content")
        
        root_file = self.source_dir / "root.txt"
        root_file.write_text("root content")
        
        worker = CopyWorker(self.source_dir, self.dest_dir)
        
        # Mock the signals
        worker.log = Mock()
        worker.progress = Mock()
        worker.finished = Mock()
        
        worker.run()
        
        # Verify nested structure was recreated
        copied_nested = self.dest_dir / "subdir" / "nested" / "nested.txt"
        copied_root = self.dest_dir / "root.txt"
        
        self.assertTrue(copied_nested.exists())
        self.assertTrue(copied_root.exists())
        self.assertEqual(copied_nested.read_text(), "nested content")
        self.assertEqual(copied_root.read_text(), "root content")

    def test_run_cancel_during_copy(self):
        """Test that cancel stops the copy operation."""
        # Create test files
        for i in range(5):
            (self.source_dir / f"file{i}.txt").write_text(f"content{i}")
        
        worker = CopyWorker(self.source_dir, self.dest_dir)
        
        # Mock the signals
        worker.log = Mock()
        worker.progress = Mock()
        worker.finished = Mock()
        
        # Set cancelled flag before running
        worker._cancelled = True
        
        worker.run()
        
        # Verify log message about cancellation
        worker.log.emit.assert_called_with("Copy cancelled.")
        # Verify finished was not called when cancelled
        worker.finished.emit.assert_not_called()

    def test_run_with_error(self):
        """Test error handling when copy fails."""
        worker = CopyWorker(self.source_dir, self.dest_dir)
        
        # Mock the signals
        worker.error = Mock()
        
        # Mock rglob to raise an exception
        with patch.object(Path, 'rglob', side_effect=PermissionError("Permission denied")):
            worker.run()
        
        # Verify error signal was emitted
        worker.error.emit.assert_called_once()
        call_args = worker.error.emit.call_args[0][0]
        self.assertIn("Permission denied", call_args)

    def test_progress_calculation(self):
        """Test that progress is calculated correctly."""
        # Create 10 test files
        for i in range(10):
            (self.source_dir / f"file{i}.txt").write_text(f"content{i}")
        
        worker = CopyWorker(self.source_dir, self.dest_dir)
        
        # Mock the signals
        worker.log = Mock()
        worker.progress = Mock()
        worker.finished = Mock()
        
        worker.run()
        
        # Verify progress percentages are correct
        progress_calls = worker.progress.emit.call_args_list
        self.assertEqual(len(progress_calls), 10)
        
        # Verify last call is 100%
        self.assertEqual(progress_calls[-1][0][0], 100)

    def test_log_messages_for_each_file(self):
        """Test that a log message is emitted for each copied file."""
        # Create 3 test files
        for i in range(3):
            (self.source_dir / f"file{i}.txt").write_text(f"content{i}")
        
        worker = CopyWorker(self.source_dir, self.dest_dir)
        
        # Mock the signals
        worker.log = Mock()
        worker.progress = Mock()
        worker.finished = Mock()
        
        worker.run()
        
        # Verify log message for each file
        self.assertEqual(worker.log.emit.call_count, 3)

    def test_file_metadata_preserved(self):
        """Test that file metadata is preserved during copy."""
        # Create a test file
        test_file = self.source_dir / "test.txt"
        test_file.write_text("test content")
        
        # Modify the modification time
        import os
        import time
        old_time = time.time() - 1000
        os.utime(test_file, (old_time, old_time))
        original_stat = test_file.stat()
        
        worker = CopyWorker(self.source_dir, self.dest_dir)
        worker.log = Mock()
        worker.progress = Mock()
        worker.finished = Mock()
        
        worker.run()
        
        # Verify metadata was preserved (shutil.copy2 should do this)
        copied_file = self.dest_dir / "test.txt"
        copied_stat = copied_file.stat()
        
        # Check that modification times are close (allowing small time differences)
        self.assertAlmostEqual(original_stat.st_mtime, copied_stat.st_mtime, delta=1)


if __name__ == "__main__":
    unittest.main()
