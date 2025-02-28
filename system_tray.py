"""
System tray integration for Medical Text Extractor using pystray.
This module handles system tray functionality including menu creation,
icon handling, and application control.
"""

import os
import sys
import threading
import pystray
import shutil
from pathlib import Path
from PIL import Image, ImageDraw
from config.config import Config
from utils.logger import get_logger

# Try to import cairosvg for SVG conversion
try:
    import cairosvg
    CAIROSVG_AVAILABLE = True
except ImportError:
    CAIROSVG_AVAILABLE = False
    logger = get_logger(__name__)
    logger.warning("cairosvg is not installed. SVG to PNG conversion will use fallback method.")

# Initialize logger
if 'logger' not in locals():
    logger = get_logger(__name__)
    
# Create resources directory if it doesn't exist
def ensure_resources_dir():
    """Ensure the resources directory exists"""
    resources_dir = Path("resources")
    resources_dir.mkdir(exist_ok=True)
    return resources_dir

class SystemTray:
    """
    Manages the system tray icon and menu for the Medical Text Extractor application.
    Provides user access to application functions while running in the background.
    """
    
    def __init__(self, app_controller=None):
        """
        Initialize the system tray handler.
        
        Args:
            app_controller: The main application controller that handles starting/stopping monitoring
        """
        self.app_controller = app_controller
        self.config = Config()
        self.monitoring_active = False
        self.icon = None
        self.setup_icon()
        
    def setup_icon(self):
        """Create the system tray icon"""
        # Create a simple icon - a colored circle
        icon_image = self.create_icon_image()
        
        # Create the menu items
        menu_items = self.create_menu()
        
        # Create the icon
        self.icon = pystray.Icon(
            "MedicalTextExtractor",
            icon_image,
            "Medical Text Extractor",
            menu=menu_items
        )
        
    def convert_svg_to_png(svg_path, png_path=None, width=64, height=64):
        """Convert SVG to PNG using cairosvg or a fallback method"""
        if png_path is None:
            # Create PNG path in resources directory with same name
            resources_dir = ensure_resources_dir()
            png_path = resources_dir / f"{Path(svg_path).stem}.png"
            
        # If PNG exists and is newer than SVG, use existing PNG
        if os.path.exists(png_path) and os.path.getmtime(png_path) > os.path.getmtime(svg_path):
            logger.debug(f"Using existing PNG: {png_path}")
            return png_path
            
        if CAIROSVG_AVAILABLE:
            try:
                logger.info(f"Converting SVG to PNG using cairosvg: {svg_path} -> {png_path}")
                cairosvg.svg2png(url=svg_path, write_to=str(png_path), output_width=width, output_height=height)
                return png_path
            except Exception as e:
                logger.error(f"Failed to convert SVG to PNG using cairosvg: {e}")
        else:
            logger.warning("Using fallback SVG conversion method. Install cairosvg for better results.")
            
        # Fallback: Try to find a compatible program to convert SVG to PNG
        try:
            # Try Inkscape if available
            from shutil import which
            inkscape_path = which("inkscape")
            if inkscape_path:
                import subprocess
                logger.info(f"Converting SVG to PNG using Inkscape: {svg_path} -> {png_path}")
                subprocess.run([
                    inkscape_path, 
                    "--export-filename", str(png_path),
                    "--export-width", str(width),
                    "--export-height", str(height),
                    str(svg_path)
                ], check=True)
                return png_path
        except Exception as e:
            logger.error(f"Failed to convert SVG to PNG using fallback method: {e}")
        
        logger.error(f"Could not convert SVG to PNG: {svg_path}")
        return None
            
    def create_icon_image(self):
        """Create a simple icon for the system tray"""
        # Check if pharmacy-symbol.svg exists
        pharmacy_symbol_path = Path(r"C:\Users\torgn\Downloads\pharmacy-symbol.svg")
        if pharmacy_symbol_path.exists():
            try:
                # Ensure resources directory exists
                resources_dir = ensure_resources_dir()
                
                # Copy the SVG to resources directory if it doesn't exist
                svg_dest = resources_dir / "pharmacy-symbol.svg"
                if not svg_dest.exists():
                    shutil.copy(pharmacy_symbol_path, svg_dest)
                    logger.info(f"Copied pharmacy symbol to resources directory: {svg_dest}")
                
                # Convert SVG to PNG
                png_path = convert_svg_to_png(svg_dest)
                if png_path and os.path.exists(png_path):
                    logger.info(f"Using pharmacy symbol as system tray icon: {png_path}")
                    return Image.open(png_path)
            except Exception as e:
                logger.error(f"Failed to load pharmacy symbol icon: {e}")
        
        # Check if a custom icon exists in config
        icon_path = self.config.get('system_tray', 'icon_path')
        if icon_path and os.path.exists(icon_path):
            try:
                # Check if it's an SVG file
                if icon_path.lower().endswith('.svg'):
                    png_path = convert_svg_to_png(icon_path)
                    if png_path and os.path.exists(png_path):
                        return Image.open(png_path)
                else:
                    return Image.open(icon_path)
            except Exception as e:
                logger.error(f"Failed to load custom icon: {e}")
        
        # Create a default icon - a colored circle
        width = 64
        height = 64
        color = self.config.get('system_tray', 'icon_color', fallback='#00AA00')
        
        image = Image.new('RGB', (width, height), color='white')
        dc = ImageDraw.Draw(image)
        dc.ellipse((5, 5, width-5, height-5), fill=color)
        
        return image
        
    def create_menu(self):
        """Create the system tray menu"""
        return pystray.Menu(
            pystray.MenuItem(
                "Start Monitoring", 
                self.on_start_monitoring,
                checked=lambda item: self.monitoring_active,
                radio=True
            ),
            pystray.MenuItem(
                "Stop Monitoring", 
                self.on_stop_monitoring,
                checked=lambda item: not self.monitoring_active,
                radio=True
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Search Database", self.on_search_database),
            pystray.MenuItem("View History", self.on_view_history),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Settings", self.on_open_settings),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Exit", self.on_exit)
        )
        
    def on_start_monitoring(self, icon, item):
        """Start the screenshot monitoring process"""
        try:
            if self.app_controller and not self.monitoring_active:
                self.app_controller.start_monitoring()
                self.monitoring_active = True
                logger.info("Screenshot monitoring started")
                
                # Update icon to reflect active status
                if self.config.get('system_tray', 'change_icon_when_active', fallback=True):
                    active_color = self.config.get('system_tray', 'active_icon_color', fallback='#00FF00')
                    self.update_icon_color(active_color)
        except Exception as e:
            logger.error(f"Failed to start monitoring: {e}")
            
    def on_stop_monitoring(self, icon, item):
        """Stop the screenshot monitoring process"""
        try:
            if self.app_controller and self.monitoring_active:
                self.app_controller.stop_monitoring()
                self.monitoring_active = False
                logger.info("Screenshot monitoring stopped")
                
                # Update icon to reflect inactive status
                if self.config.get('system_tray', 'change_icon_when_active', fallback=True):
                    inactive_color = self.config.get('system_tray', 'icon_color', fallback='#00AA00')
                    self.update_icon_color(inactive_color)
        except Exception as e:
            logger.error(f"Failed to stop monitoring: {e}")
            
    def on_search_database(self, icon, item):
        """Open the database search dialog"""
        try:
            if self.app_controller:
                # This would typically open a GUI dialog or command-line interface
                self.app_controller.open_search_interface()
                logger.info("Database search interface opened")
        except Exception as e:
            logger.error(f"Failed to open search interface: {e}")
            
    def on_view_history(self, icon, item):
        """View detection history"""
        try:
            if self.app_controller:
                self.app_controller.open_history_view()
                logger.info("History view opened")
        except Exception as e:
            logger.error(f"Failed to open history view: {e}")
            
    def on_open_settings(self, icon, item):
        """Open the settings dialog"""
        try:
            if self.app_controller:
                self.app_controller.open_settings()
                logger.info("Settings dialog opened")
        except Exception as e:
            logger.error(f"Failed to open settings: {e}")
            
    def on_exit(self, icon, item):
        """Exit the application"""
        logger.info("Exiting application from system tray")
        icon.stop()
        if self.app_controller:
            self.app_controller.shutdown()
        
    def update_icon_color(self, color):
        """Update the icon color to reflect active/inactive status"""
        if self.icon:
            new_image = self.create_custom_icon(color)
            self.icon.icon = new_image
            
    def create_custom_icon(self, color):
        """Create a custom icon with the specified color"""
        width = 64
        height = 64
        
        image = Image.new('RGB', (width, height), color='white')
        dc = ImageDraw.Draw(image)
        dc.ellipse((5, 5, width-5, height-5), fill=color)
        
        return image
        
    def run(self):
        """Run the system tray icon in a separate thread"""
        logger.info("Starting system tray")
        if self.icon:
            self.icon.run()
            
    def run_detached(self):
        """Run the system tray in a separate thread"""
        thread = threading.Thread(target=self.run)
        thread.daemon = True
        thread.start()
        return thread
        
    def stop(self):
        """Stop the system tray icon"""
        if self.icon:
            self.icon.stop()
            logger.info("System tray stopped")


# Example usage
if __name__ == "__main__":
    # This would be a demo of the system tray in isolation
    class MockController:
        def start_monitoring(self):
            print("Mock: Starting monitoring")
            
        def stop_monitoring(self):
            print("Mock: Stopping monitoring")
            
        def open_search_interface(self):
            print("Mock: Opening search interface")
            
        def open_history_view(self):
            print("Mock: Opening history view")
            
        def open_settings(self):
            print("Mock: Opening settings")
            
        def shutdown(self):
            print("Mock: Shutting down application")
            sys.exit(0)
            
    # Create and run the system tray
    mock_controller = MockController()
    tray = SystemTray(mock_controller)
    tray.run()

