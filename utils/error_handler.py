"""
Error handler module for the Medical Text Extractor application.
This module provides functionality to handle and log errors in a consistent way.
"""

import logging
import sys
import traceback
from typing import Optional, Dict, Any, Union

# Assuming the Notifier class is in the same utils package
from utils.notifications import Notifier

class ErrorHandler:
    """
    A class to handle and log errors, and display error notifications to the user.
    """
    def __init__(self, logger: Optional[logging.Logger] = None, show_notifications: bool = True):
        """
        Initialize the ErrorHandler with a logger and notification settings.
        
        Args:
            logger: A logging.Logger instance. If None, a new logger will be created.
            show_notifications: Whether to show notifications to the user.
        """
        self.logger = logger or logging.getLogger(__name__)
        self.show_notifications = show_notifications
        self.notifier = Notifier() if show_notifications else None
    
    def handle_error(self, error: Exception, context: Optional[Dict[str, Any]] = None, 
                    show_notification: Optional[bool] = None) -> None:
        """
        Handle a general error by logging it and optionally showing a notification.
        
        Args:
            error: The exception that occurred.
            context: Additional context about where/why the error occurred.
            show_notification: Override the default notification setting.
        """
        error_type = type(error).__name__
        error_message = str(error)
        
        # Add context to the error message if provided
        context_str = f" | Context: {context}" if context else ""
        
        # Log the error with traceback
        self.logger.error(f"{error_type}: {error_message}{context_str}", exc_info=True)
        
        # Determine whether to show a notification
        should_notify = self.show_notifications if show_notification is None else show_notification
        
        # Show a notification if enabled
        if should_notify and self.notifier:
            notification_message = f"{error_type}: {error_message}"
            self.notifier.error(title="Application Error", message=notification_message)
    
    def handle_validation_error(self, message: str, details: Optional[str] = None, 
                            show_notification: Optional[bool] = None) -> None:
        """
        Handle a validation error (invalid user input, configuration, etc.).
        
        Args:
            message: The validation error message.
            details: Additional details about the validation error.
            show_notification: Override the default notification setting.
        """
        # Prepare the log message
        log_message = f"Validation Error: {message}"
        if details:
            log_message += f" | Details: {details}"
        
        # Log the validation error
        self.logger.warning(log_message)
        
        # Determine whether to show a notification
        should_notify = self.show_notifications if show_notification is None else show_notification
        
        # Show a notification if enabled
        if should_notify and self.notifier:
            notification_message = message
            if details:
                notification_message += f"\n{details}"
            self.notifier.warning(title="Validation Error", message=notification_message)
    
    def handle_ocr_error(self, message: str, image_path: Optional[str] = None, 
                    show_notification: Optional[bool] = None) -> None:
        """
        Handle an OCR-related error.
        
        Args:
            message: The OCR error message.
            image_path: Path to the image that failed OCR.
            show_notification: Override the default notification setting.
        """
        # Prepare the log message
        log_message = f"OCR Error: {message}"
        if image_path:
            log_message += f" | Image: {image_path}"
        
        # Log the OCR error
        self.logger.error(log_message)
        
        # Determine whether to show a notification
        should_notify = self.show_notifications if show_notification is None else show_notification
        
        # Show a notification if enabled
        if should_notify and self.notifier:
            notification_message = message
            if image_path:
                notification_message += f"\nImage: {image_path}"
            self.notifier.error(title="OCR Error", message=notification_message)
    
    def handle_database_error(self, error: Exception, operation: Optional[str] = None, 
                            show_notification: Optional[bool] = None) -> None:
        """
        Handle a database-related error.
        
        Args:
            error: The database exception that occurred.
            operation: Description of the database operation that failed.
            show_notification: Override the default notification setting.
        """
        # Prepare context information
        context = {"operation": operation} if operation else {}
        
        # Log the database error with context
        self.handle_error(error, context, show_notification)
        
        # If we want specialized database error handling, we could implement it here
    
    def handle_critical_error(self, error: Exception, should_exit: bool = False) -> None:
        """
        Handle a critical error that might require exiting the application.
        
        Args:
            error: The critical exception that occurred.
            should_exit: Whether to exit the application after handling the error.
        """
        error_type = type(error).__name__
        error_message = str(error)
        
        # Log the critical error
        self.logger.critical(f"CRITICAL ERROR - {error_type}: {error_message}", exc_info=True)
        
        # Always show a notification for critical errors if a notifier is available
        if self.notifier:
            notification_message = f"A critical error has occurred: {error_message}"
            if should_exit:
                notification_message += "\nThe application will now exit."
            self.notifier.error(title="Critical Error", message=notification_message)
        
        # Exit the application if requested
        if should_exit:
            self.logger.critical("Exiting application due to critical error")
            sys.exit(1)
    
    def format_error_message(self, error: Exception, include_traceback: bool = False) -> str:
        """
        Format an error message for display or logging.
        
        Args:
            error: The exception to format.
            include_traceback: Whether to include the traceback in the formatted message.
        
        Returns:
            A formatted error message string.
        """
        error_type = type(error).__name__
        error_message = str(error)
        
        formatted_message = f"{error_type}: {error_message}"
        
        if include_traceback:
            tb = traceback.format_exception(type(error), error, error.__traceback__)
            formatted_message += "\n\nTraceback:\n" + "".join(tb)
        
        return formatted_message
    
    @staticmethod
    def get_error_context(locals_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract useful context information from a locals dictionary.
        
        Args:
            locals_dict: The locals() dictionary from the error context.
        
        Returns:
            A dictionary with relevant context information.
        """
        # Filter out private variables and common builtins
        context = {}
        for key, value in locals_dict.items():
            if not key.startswith('__') and key != 'self' and key != 'cls':
                # Convert complex objects to strings to avoid serialization issues
                try:
                    if not isinstance(value, (str, int, float, bool, type(None))):
                        context[key] = str(value)
                    else:
                        context[key] = value
                except:
                    context[key] = f"<Unable to convert {type(value).__name__}>"
        
        return context

