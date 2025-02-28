import os
import sys
import winreg
import logging
import atexit
from pathlib import Path

class StartupService:
    """
    Handles startup and shutdown procedures for the Medical Text Extractor application.
    Enables automatic startup with Windows and proper resource cleanup on exit.
    """
    
    def __init__(self, app_name="MedicalTextExtractor", main_script="main.py", log=None):
        """
        Initialize the startup service.
        
        Args:
            app_name (str): Name of the application
            main_script (str): Name of the main script to execute on startup
            log (logging.Logger, optional): Logger instance
        """
        self.app_name = app_name
        self.main_script = main_script
        self.logger = log or logging.getLogger(__name__)
        self.startup_key = r"Software\Microsoft\Windows\CurrentVersion\Run"
        
        # Register the cleanup handler
        atexit.register(self.cleanup)
    
    def enable_autostart(self):
        """
        Enable application to start automatically when Windows boots.
        Returns True if successful, False otherwise.
        """
        try:
            # Get the full path to the script
            script_path = os.path.abspath(self.main_script)
            pythonw_path = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
            
            # Create the command to run the script with pythonw (no console window)
            cmd = f'"{pythonw_path}" "{script_path}"'
            
            # Open the registry key
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER, 
                self.startup_key, 
                0, 
                winreg.KEY_WRITE
            ) as key:
                # Set the value
                winreg.SetValueEx(key, self.app_name, 0, winreg.REG_SZ, cmd)
            
            self.logger.info(f"Application '{self.app_name}' enabled for autostart")
            return True
        except Exception as e:
            self.logger.error(f"Failed to enable autostart: {e}")
            return False
    
    def disable_autostart(self):
        """
        Disable application from starting automatically.
        Returns True if successful, False otherwise.
        """
        try:
            # Open the registry key
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER, 
                self.startup_key, 
                0, 
                winreg.KEY_WRITE
            ) as key:
                # Delete the value
                winreg.DeleteValue(key, self.app_name)
            
            self.logger.info(f"Application '{self.app_name}' disabled from autostart")
            return True
        except FileNotFoundError:
            # Key doesn't exist, so already disabled
            self.logger.info(f"Application '{self.app_name}' not found in autostart")
            return True
        except Exception as e:
            self.logger.error(f"Failed to disable autostart: {e}")
            return False
    
    def is_autostart_enabled(self):
        """
        Check if autostart is enabled for the application.
        Returns True if enabled, False otherwise.
        """
        try:
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER, 
                self.startup_key, 
                0, 
                winreg.KEY_READ
            ) as key:
                winreg.QueryValueEx(key, self.app_name)
            return True
        except:
            return False
    
    def create_shortcut(self, target_directory=None):
        """
        Create a shortcut to the application in the specified directory.
        If directory is None, create in the Start Menu.
        
        Returns True if successful, False otherwise.
        """
        try:
            import pythoncom
            from win32com.client import Dispatch
            
            if target_directory is None:
                # Use Start Menu Programs folder
                target_directory = os.path.join(
                    os.environ["APPDATA"], 
                    r"Microsoft\Windows\Start Menu\Programs"
                )
            
            # Ensure directory exists
            os.makedirs(target_directory, exist_ok=True)
            
            # Get paths
            script_path = os.path.abspath(self.main_script)
            shortcut_path = os.path.join(target_directory, f"{self.app_name}.lnk")
            
            # Create shortcut
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath = sys.executable
            shortcut.Arguments = f'"{script_path}"'
            shortcut.WorkingDirectory = os.path.dirname(script_path)
            shortcut.IconLocation = sys.executable
            shortcut.save()
            
            self.logger.info(f"Created shortcut at {shortcut_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to create shortcut: {e}")
            return False
    
    def cleanup(self):
        """
        Perform cleanup operations when the application exits.
        This is registered to run automatically via atexit.
        """
        try:
            self.logger.info("Performing cleanup operations before shutdown")
            # Add any cleanup operations here:
            # - Close database connections
            # - Save application state
            # - Release system resources
            
            # Example: Create a sentinel file that indicates clean shutdown
            Path(".clean_shutdown").touch()
            
            self.logger.info("Cleanup completed successfully")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")

# Usage example:
if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("startup_service")
    
    # Create service instance
    service = StartupService(log=logger)
    
    # Example commands:
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        if cmd == "enable":
            service.enable_autostart()
        elif cmd == "disable":
            service.disable_autostart()
        elif cmd == "status":
            status = "enabled" if service.is_autostart_enabled() else "disabled"
            print(f"Autostart is {status}")
        elif cmd == "shortcut":
            service.create_shortcut()
        else:
            print("Unknown command. Use: enable, disable, status, or shortcut")

