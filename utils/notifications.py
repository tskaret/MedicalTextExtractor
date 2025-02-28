import os
import logging

# Try to import win10toast, but fall back to using print statements if not available
try:
    from win10toast import ToastNotifier
    TOAST_AVAILABLE = True
except ImportError:
    TOAST_AVAILABLE = False
    logging.warning("win10toast package not available, falling back to print statements for notifications")

class Notifier:
    """
    A class to handle system notifications using Windows toast notifications.
    Provides methods for different types of notifications (info, success, warning, error).
    """
    
    def __init__(self, app_name="Medical Text Extractor"):
        """
        Initialize the Notifier with the application name.
        
        Args:
            app_name (str): Name of the application to display in notifications
        """
        self.app_name = app_name
        self.logger = logging.getLogger(__name__)
        
        # Initialize toaster if available, otherwise set to None
        self.toaster = ToastNotifier() if TOAST_AVAILABLE else None
        
        if not TOAST_AVAILABLE:
            self.logger.info("Using print fallback instead of toast notifications")
        
        # Default duration in seconds
        self.default_duration = 5
        
        # Try to load icon if it exists
        self.icon_path = None
        possible_icon_paths = [
            os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "icon.ico"),
            os.path.join(os.path.dirname(os.path.dirname(__file__)), "icon.ico")
        ]
        
        for path in possible_icon_paths:
            if os.path.exists(path):
                self.icon_path = path
                break
    
    def info(self, message, title=None, duration=None):
        """
        Display an information notification.
        
        Args:
            message (str): The notification message
            title (str, optional): The notification title
            duration (int, optional): How long the notification should be displayed
        """
        if title is None:
            title = f"{self.app_name} - Information"
        self._show_notification(message, title, duration)
        self.logger.info(f"INFO: {message}")
        
    def success(self, message, title=None, duration=None):
        """
        Display a success notification.
        
        Args:
            message (str): The notification message
            title (str, optional): The notification title
            duration (int, optional): How long the notification should be displayed
        """
        if title is None:
            title = f"{self.app_name} - Success"
        self._show_notification(message, title, duration)
        self.logger.info(f"SUCCESS: {message}")
        
    def warning(self, message, title=None, duration=None):
        """
        Display a warning notification.
        
        Args:
            message (str): The notification message
            title (str, optional): The notification title
            duration (int, optional): How long the notification should be displayed
        """
        if title is None:
            title = f"{self.app_name} - Warning"
        self._show_notification(message, title, duration)
        self.logger.warning(f"WARNING: {message}")
        
    def error(self, message, title=None, duration=None):
        """
        Display an error notification.
        
        Args:
            message (str): The notification message
            title (str, optional): The notification title
            duration (int, optional): How long the notification should be displayed
        """
        if title is None:
            title = f"{self.app_name} - Error"
        self._show_notification(message, title, duration)
        self.logger.error(f"ERROR: {message}")
        
    def _show_notification(self, message, title, duration=None):
        """
        Internal method to show a notification.
        
        Args:
            message (str): The notification message
            title (str): The notification title
            duration (int, optional): How long the notification should be displayed
        """
        if duration is None:
            duration = self.default_duration
            
        try:
            if TOAST_AVAILABLE and self.toaster:
                self.toaster.show_toast(
                    title=title,
                    msg=message,
                    icon_path=self.icon_path,
                    duration=duration,
                    threaded=True  # Run in a separate thread to avoid blocking
                )
            else:
                # Fallback to print statements if win10toast is not available
                print(f"\n{'='*50}\n{title}\n{'-'*50}\n{message}\n{'='*50}\n")
        except Exception as e:
            self.logger.error(f"Failed to show notification: {str(e)}")
            
    def set_default_duration(self, seconds):
        """
        Set the default duration for notifications.
        
        Args:
            seconds (int): Duration in seconds
        """
        self.default_duration = seconds
        
    def set_icon_path(self, path):
        """
        Set a custom icon path for notifications.
        
        Args:
            path (str): Path to the icon file
        """
        if os.path.exists(path):
            self.icon_path = path
            return True
        else:
            self.logger.warning(f"Icon path does not exist: {path}")
            return False

