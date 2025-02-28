import io
import time
import threading
from pynput import keyboard
from PIL import Image, ImageGrab
import pyperclip

class ScreenshotMonitor:
    """
    A class to monitor for screenshots and clipboard image data.
    
    This class provides functionality to:
    1. Detect when PrintScreen key is pressed
    2. Monitor the clipboard for new image data
    3. Run in the background as a daemon thread
    """
    
    def __init__(self, on_screenshot_callback=None):
        """
        Initialize the screenshot monitor.
        
        Args:
            on_screenshot_callback: Function to call when a screenshot is detected.
                The function should accept an Image object as its parameter.
        """
        self.on_screenshot_callback = on_screenshot_callback
        self.running = False
        self.monitor_thread = None
        self.keyboard_listener = None
        self.last_clipboard_image = None
        
    def _on_key_press(self, key):
        """Handle key press events to detect PrintScreen."""
        try:
            # Check for PrintScreen key
            if key == keyboard.Key.print_screen:
                self._check_clipboard_for_image()
        except Exception as e:
            print(f"Error in key press handler: {e}")
            
    def _check_clipboard_for_image(self):
        """Check if clipboard contains image data and process it."""
        try:
            # Small delay to let the system put the screenshot in clipboard
            time.sleep(0.1)
            
            # Get image from clipboard
            img = ImageGrab.grabclipboard()
            
            # Check if clipboard contains an image and it's different from the last one
            if img and isinstance(img, Image.Image):
                # Compare with last image if exists
                if self.last_clipboard_image is None or img.size != self.last_clipboard_image.size:
                    self.last_clipboard_image = img
                    self._process_screenshot(img)
                else:
                    # Additional check - compare image data
                    current_bytes = io.BytesIO()
                    img.save(current_bytes, format='PNG')
                    current_bytes = current_bytes.getvalue()
                    
                    last_bytes = io.BytesIO()
                    self.last_clipboard_image.save(last_bytes, format='PNG')
                    last_bytes = last_bytes.getvalue()
                    
                    if current_bytes != last_bytes:
                        self.last_clipboard_image = img
                        self._process_screenshot(img)
        except Exception as e:
            print(f"Error checking clipboard for image: {e}")
            
    def _process_screenshot(self, img):
        """Process a detected screenshot."""
        if self.on_screenshot_callback:
            self.on_screenshot_callback(img)
        else:
            print("Screenshot detected, but no callback is registered.")
            
    def _monitor_clipboard(self):
        """Background thread to periodically check clipboard for new images."""
        while self.running:
            self._check_clipboard_for_image()
            time.sleep(1)  # Check every second
            
    def start(self):
        """Start monitoring for screenshots and clipboard changes."""
        if self.running:
            print("Screenshot monitor is already running.")
            return
            
        self.running = True
        
        # Start keyboard listener for PrintScreen key
        self.keyboard_listener = keyboard.Listener(on_press=self._on_key_press)
        self.keyboard_listener.start()
        
        # Start clipboard monitoring thread
        self.monitor_thread = threading.Thread(
            target=self._monitor_clipboard,
            daemon=True
        )
        self.monitor_thread.start()
        
        print("Screenshot monitor started.")
        
    def stop(self):
        """Stop monitoring for screenshots."""
        if not self.running:
            print("Screenshot monitor is not running.")
            return
            
        self.running = False
        
        # Stop keyboard listener
        if self.keyboard_listener:
            self.keyboard_listener.stop()
            self.keyboard_listener = None
            
        # Monitor thread will stop itself since it's a daemon
        self.monitor_thread = None
        
        print("Screenshot monitor stopped.")
        
    def is_running(self):
        """Check if the monitor is currently running."""
        return self.running


# Example usage
if __name__ == "__main__":
    def screenshot_handler(img):
        print(f"Screenshot detected! Size: {img.size}")
        # Save the screenshot for testing
        img.save("last_screenshot.png")
        
    # Create and start the monitor
    monitor = ScreenshotMonitor(on_screenshot_callback=screenshot_handler)
    monitor.start()
    
    try:
        print("Monitoring for screenshots. Press Ctrl+C to exit.")
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        monitor.stop()
        print("Screenshot monitoring stopped.")

