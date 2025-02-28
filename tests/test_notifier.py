import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add parent directory to path so we can import the utils module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.notifications import Notifier


class TestNotifier(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method runs."""
        self.notifier = Notifier()
    
    def tearDown(self):
        """Tear down test fixtures after each test method runs."""
        self.notifier = None
    
    @patch('win10toast.ToastNotifier')
    def test_init(self, mock_toast):
        """Test that the Notifier initializes correctly."""
        notifier = Notifier()
        mock_toast.assert_called_once()
        self.assertIsNotNone(notifier.toaster)
    
    @patch('utils.notifications.Notifier._show_notification')
    def test_info_notification(self, mock_show):
        """Test that info notifications use the correct parameters."""
        title = "Test Info"
        message = "This is an info message"
        self.notifier.info(title, message)
        mock_show.assert_called_once_with(title, message, duration=5, icon_path=None)
    
    @patch('utils.notifications.Notifier._show_notification')
    def test_success_notification(self, mock_show):
        """Test that success notifications use the correct parameters."""
        title = "Test Success"
        message = "This is a success message"
        self.notifier.success(title, message)
        mock_show.assert_called_once_with(title, message, duration=5, icon_path=None)
    
    @patch('utils.notifications.Notifier._show_notification')
    def test_warning_notification(self, mock_show):
        """Test that warning notifications use the correct parameters."""
        title = "Test Warning"
        message = "This is a warning message"
        self.notifier.warning(title, message)
        mock_show.assert_called_once_with(title, message, duration=7, icon_path=None)
    
    @patch('utils.notifications.Notifier._show_notification')
    def test_error_notification(self, mock_show):
        """Test that error notifications use the correct parameters."""
        title = "Test Error"
        message = "This is an error message"
        self.notifier.error(title, message)
        mock_show.assert_called_once_with(title, message, duration=10, icon_path=None)
    
    @patch('win10toast.ToastNotifier.show_toast')
    def test_show_notification(self, mock_show_toast):
        """Test that _show_notification calls the Windows toast notification correctly."""
        title = "Test Notification"
        message = "This is a test message"
        duration = 3
        icon_path = "test_icon.ico"
        
        self.notifier._show_notification(title, message, duration, icon_path)
        
        mock_show_toast.assert_called_once_with(
            title, 
            message, 
            icon_path=icon_path, 
            duration=duration,
            threaded=True
        )
    
    @patch('utils.notifications.Notifier._show_notification')
    def test_custom_duration(self, mock_show):
        """Test that custom durations are used correctly."""
        title = "Test Custom Duration"
        message = "This message has a custom duration"
        custom_duration = 15
        
        self.notifier.info(title, message, duration=custom_duration)
        mock_show.assert_called_once_with(title, message, duration=custom_duration, icon_path=None)
    
    @patch('utils.notifications.Notifier._show_notification')
    def test_custom_icon(self, mock_show):
        """Test that custom icons are used correctly."""
        title = "Test Custom Icon"
        message = "This message has a custom icon"
        custom_icon = "custom_icon.ico"
        
        self.notifier.info(title, message, icon_path=custom_icon)
        mock_show.assert_called_once_with(title, message, duration=5, icon_path=custom_icon)


if __name__ == '__main__':
    unittest.main()

