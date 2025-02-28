import unittest
from unittest.mock import patch, MagicMock, call
import logging
import os
import tempfile
import sys

# Add parent directory to path to import utils.logger
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.logger import Logger


class TestLogger(unittest.TestCase):
    """Test cases for the Logger class in utils/logger.py"""
    
    def setUp(self):
        """Set up test environment before each test"""
        # Create a temporary directory for log files
        self.temp_dir = tempfile.TemporaryDirectory()
        self.log_path = os.path.join(self.temp_dir.name, "test.log")
        
        # Reset the logging configuration before each test
        logging.root.handlers = []
        logging.root.setLevel(logging.NOTSET)
    
    def tearDown(self):
        """Clean up after each test"""
        self.temp_dir.cleanup()
    
    @patch('logging.FileHandler')
    @patch('logging.StreamHandler')
    def test_init_default_settings(self, mock_stream_handler, mock_file_handler):
        """Test that Logger initializes with default settings"""
        # Setup mock handlers
        mock_stream_handler.return_value = MagicMock()
        mock_file_handler.return_value = MagicMock()
        
        # Create logger with default settings
        logger = Logger(log_path=self.log_path)
        
        # Verify logger level set to INFO
        self.assertEqual(logger.logger.level, logging.INFO)
        
        # Verify file handler created with correct path
        mock_file_handler.assert_called_once_with(self.log_path)
        
        # Verify both handlers added to logger
        self.assertEqual(len(logger.logger.handlers), 2)
        
        # Verify formatters set correctly
        for handler in mock_stream_handler.return_value, mock_file_handler.return_value:
            formatter = handler.setFormatter.call_args[0][0]
            self.assertIsInstance(formatter, logging.Formatter)
    
    @patch('logging.FileHandler')
    @patch('logging.StreamHandler')
    def test_custom_log_level(self, mock_stream_handler, mock_file_handler):
        """Test that Logger respects custom log level settings"""
        # Setup mock handlers
        mock_stream_handler.return_value = MagicMock()
        mock_file_handler.return_value = MagicMock()
        
        # Create logger with DEBUG level
        logger = Logger(log_path=self.log_path, level=logging.DEBUG)
        
        # Verify logger level set to DEBUG
        self.assertEqual(logger.logger.level, logging.DEBUG)
        
        # Verify handlers have correct level
        mock_stream_handler.return_value.setLevel.assert_called_with(logging.DEBUG)
        mock_file_handler.return_value.setLevel.assert_called_with(logging.DEBUG)
    
    @patch('logging.FileHandler')
    @patch('logging.StreamHandler')
    def test_disable_console_output(self, mock_stream_handler, mock_file_handler):
        """Test that Logger can disable console output"""
        # Setup mock handlers
        mock_stream_handler.return_value = MagicMock()
        mock_file_handler.return_value = MagicMock()
        
        # Create logger with console output disabled
        logger = Logger(log_path=self.log_path, console_output=False)
        
        # Verify only file handler added (no console handler)
        mock_stream_handler.assert_not_called()
        mock_file_handler.assert_called_once()
        self.assertEqual(len(logger.logger.handlers), 1)
    
    @patch('logging.FileHandler')
    @patch('logging.StreamHandler')
    def test_custom_format(self, mock_stream_handler, mock_file_handler):
        """Test that Logger uses custom format when provided"""
        # Setup mock handlers
        mock_stream_handler.return_value = MagicMock()
        mock_file_handler.return_value = MagicMock()
        
        # Custom format string
        custom_format = "%(asctime)s - CUSTOM - %(message)s"
        
        # Create logger with custom format
        logger = Logger(log_path=self.log_path, format_str=custom_format)
        
        # Get formatter passed to setFormatter
        formatter = mock_file_handler.return_value.setFormatter.call_args[0][0]
        
        # Verify custom format used
        self.assertEqual(formatter._fmt, custom_format)
    
    def test_log_messages(self):
        """Test that Logger correctly logs messages at different levels"""
        # Create actual logger writing to temporary file
        logger = Logger(log_path=self.log_path)
        
        # Log messages at different levels
        test_message = "Test log message"
        logger.logger.debug(f"DEBUG: {test_message}")
        logger.logger.info(f"INFO: {test_message}")
        logger.logger.warning(f"WARNING: {test_message}")
        logger.logger.error(f"ERROR: {test_message}")
        logger.logger.critical(f"CRITICAL: {test_message}")
        
        # Read log file content
        with open(self.log_path, 'r') as f:
            log_content = f.read()
        
        # Default level is INFO, so DEBUG message should not be present
        self.assertNotIn(f"DEBUG: {test_message}", log_content)
        
        # Other messages should be present
        self.assertIn(f"INFO: {test_message}", log_content)
        self.assertIn(f"WARNING: {test_message}", log_content)
        self.assertIn(f"ERROR: {test_message}", log_content)
        self.assertIn(f"CRITICAL: {test_message}", log_content)
    
    def test_get_logger(self):
        """Test that get_logger returns the configured logger"""
        logger_instance = Logger(log_path=self.log_path)
        returned_logger = logger_instance.get_logger()
        
        # Verify the returned logger is the configured logger
        self.assertEqual(returned_logger, logger_instance.logger)


if __name__ == '__main__':
    unittest.main()

