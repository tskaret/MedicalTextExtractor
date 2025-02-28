import os
import logging
from logging.handlers import RotatingFileHandler
import datetime

class Logger:
    """
    Logger utility class for the Medical Text Extractor application.
    Provides logging functionality with configurable log levels, file handlers,
    and console handlers.
    """
    
    # Default log level for both file and console
    DEFAULT_LOG_LEVEL = logging.INFO
    
    # Default log file location and settings
    DEFAULT_LOG_DIR = "logs"
    DEFAULT_LOG_FILENAME = "medical_text_extractor.log"
    DEFAULT_MAX_BYTES = 10 * 1024 * 1024  # 10 MB
    DEFAULT_BACKUP_COUNT = 5
    
    @classmethod
    def setup(cls, log_level=None, log_file=None, console_level=None, 
            max_bytes=None, backup_count=None):
        """
        Set up the logger with the specified configuration.
        
        Args:
            log_level (int, optional): Log level for file handler. Defaults to INFO.
            log_file (str, optional): Path to log file. Defaults to logs/medical_text_extractor.log.
            console_level (int, optional): Log level for console handler. Defaults to INFO.
            max_bytes (int, optional): Maximum log file size in bytes. Defaults to 10 MB.
            backup_count (int, optional): Number of backup logs to keep. Defaults to 5.
        
        Returns:
            logging.Logger: The configured root logger.
        """
        # Set default values if not provided
        log_level = log_level or cls.DEFAULT_LOG_LEVEL
        console_level = console_level or cls.DEFAULT_LOG_LEVEL
        max_bytes = max_bytes or cls.DEFAULT_MAX_BYTES
        backup_count = backup_count or cls.DEFAULT_BACKUP_COUNT
        
        if log_file is None:
            # Create logs directory if it doesn't exist
            os.makedirs(cls.DEFAULT_LOG_DIR, exist_ok=True)
            log_file = os.path.join(cls.DEFAULT_LOG_DIR, cls.DEFAULT_LOG_FILENAME)
        
        # Configure the root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)  # Set to lowest level, handlers will filter
        
        # Remove existing handlers to avoid duplicates if setup is called multiple times
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # File handler
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(console_level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
        
        # Log setup information
        root_logger.info(f"Logger initialized at {datetime.datetime.now()}")
        root_logger.debug(f"Log file: {log_file}")
        root_logger.debug(f"File log level: {logging.getLevelName(log_level)}")
        root_logger.debug(f"Console log level: {logging.getLevelName(console_level)}")
        
        return root_logger
    
    @classmethod
    def get_logger(cls, name):
        """
        Get a logger with the specified name.
        
        Args:
            name (str): Name of the logger, typically __name__ of the module.
        
        Returns:
            logging.Logger: The logger instance.
        """
        return logging.getLogger(name)
    
    @classmethod
    def set_level(cls, level):
        """
        Set the log level for all handlers.
        
        Args:
            level (int): Log level (e.g., logging.DEBUG, logging.INFO).
        """
        root_logger = logging.getLogger()
        for handler in root_logger.handlers:
            handler.setLevel(level)
        
        root_logger.info(f"Log level changed to {logging.getLevelName(level)}")

# Usage example:
# 1. Setup logging once at the start of the application
# Logger.setup()
# 
# 2. Get logger in each module
# logger = Logger.get_logger(__name__)
# logger.debug("Debug message")
# logger.info("Info message")
# logger.warning("Warning message")
# logger.error("Error message")
# logger.critical("Critical message")

