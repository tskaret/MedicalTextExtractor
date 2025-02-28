import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.error_handler import ErrorHandler


class TestErrorHandler(unittest.TestCase):
    """
    Unit tests for the ErrorHandler class.
    """
    
    def setUp(self):
        """Set up test fixtures before each test."""
        # Create mock objects for Notifier and logger
        self.mock_notifier = MagicMock()
        self.mock_logger = MagicMock()
        
        # Create ErrorHandler instance with mocked dependencies
        self.error_handler = ErrorHandler(notifier=self.mock_notifier, logger=self.mock_logger)
    
    def test_init(self):
        """Test initialization of ErrorHandler."""
        self.assertEqual(self.error_handler.notifier, self.mock_notifier)
        self.assertEqual(self.error_handler.logger, self.mock_logger)
    
    def test_handle_error(self):
        """Test the handle_error method."""
        error = Exception("Test error")
        self.error_handler.handle_error(error, "Test operation")
        
        # Verify logger error was called
        self.mock_logger.error.assert_called_once()
        
        # Verify notifier show_error was called
        self.mock_notifier.error.assert_called_once()
        
        # Verify the error message contains the operation and error
        error_call_args = self.mock_notifier.error.call_args[0]
        self.assertIn("Test operation", error_call_args[0])
        self.assertIn("Test error", error_call_args[0])
    
    def test_handle_validation_error(self):
        """Test the handle_validation_error method."""
        error_message = "Invalid input data"
        operation = "data validation"
        
        self.error_handler.handle_validation_error(error_message, operation)
        
        # Verify logger warning was called
        self.mock_logger.warning.assert_called_once()
        
        # Verify notifier warning was called
        self.mock_notifier.warning.assert_called_once()
        
        # Verify the warning message contains the operation and error
        warning_call_args = self.mock_notifier.warning.call_args[0]
        self.assertIn(operation, warning_call_args[0])
        self.assertIn(error_message, warning_call_args[0])
    
    @patch('utils.error_handler.traceback.format_exc')
    def test_handle_critical_error(self, mock_format_exc):
        """Test the handle_critical_error method."""
        mock_format_exc.return_value = "Traceback details"
        
        try:
            # Raise an exception to test critical error handling
            raise ValueError("Test critical error")
        except Exception as e:
            self.error_handler.handle_critical_error(e, "Critical operation")
        
        # Verify logger critical was called
        self.mock_logger.critical.assert_called_once()
        
        # Verify notifier error was called with critical flag
        self.mock_notifier.error.assert_called_once()
        
        # Verify traceback was obtained
        mock_format_exc.assert_called_once()
        
        # Verify the error message contains the operation and exception
        error_call_args = self.mock_notifier.error.call_args[0]
        self.assertIn("Critical operation", error_call_args[0])
        self.assertIn("Test critical error", error_call_args[0])
    
    def test_handle_error_with_details(self):
        """Test handling errors with additional details."""
        error = Exception("Complex error")
        details = {"user": "test_user", "file": "test.txt", "operation": "read"}
        
        self.error_handler.handle_error(error, "Complex operation", details)
        
        # Verify logger error was called with details
        self.mock_logger.error.assert_called_once()
        log_message = self.mock_logger.error.call_args[0][0]
        for key, value in details.items():
            self.assertIn(key, log_message)
            self.assertIn(str(value), log_message)
        
        # Verify notifier error was called
        self.mock_notifier.error.assert_called_once()
        
    def test_handle_ocr_error(self):
        """Test the handle_ocr_error method."""
        error_message = "OCR processing failed"
        file_path = "document.pdf"
        
        self.error_handler.handle_ocr_error(error_message, file_path)
        
        # Verify logger error was called
        self.mock_logger.error.assert_called_once()
        
        # Verify notifier error was called
        self.mock_notifier.error.assert_called_once()
        
        # Verify the error message contains the file path and error message
        error_call_args = self.mock_notifier.error.call_args[0]
        self.assertIn(file_path, error_call_args[0])
        self.assertIn(error_message, error_call_args[0])
        
    def test_handle_database_error(self):
        """Test the handle_database_error method."""
        error = Exception("Database connection failed")
        operation = "database query"
        
        self.error_handler.handle_database_error(error, operation)
        
        # Verify logger error was called
        self.mock_logger.error.assert_called_once()
        
        # Verify notifier error was called
        self.mock_notifier.error.assert_called_once()
        
        # Verify the error message contains the operation and error
        error_call_args = self.mock_notifier.error.call_args[0]
        self.assertIn(operation, error_call_args[0])
        self.assertIn("Database connection failed", error_call_args[0])


if __name__ == '__main__':
    unittest.main()

