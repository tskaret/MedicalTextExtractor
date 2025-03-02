#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Enhanced Clipboard Monitor - Automatically detects images in clipboard, extracts medication information,
displays administration instructions, and provides a system tray icon for user control.
"""

import os
import sys
import time
import logging
import io
import re
import threading
import pyperclip
import subprocess
import ctypes
from PIL import ImageGrab, Image, ImageDraw
from datetime import datetime
import win32api
import win32con
import pystray

# Import the tesseract path configuration
try:
    from tesseract_path import *
except ImportError:
    pass

from improved_text_analyzer import ImprovedTextAnalyzer
from ocr_processor import OCRProcessor
from lookup_medication import lookup_medication

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('clipboard_monitor.log')
    ]
)
logger = logging.getLogger("EnhancedClipboardMonitor")

# Constants
POLL_INTERVAL = 1.0  # seconds
OUTPUT_FILE = "clipboard_results.txt"
EXTRACTED_TEXT_FILE = "extracted_text.txt"
USE_WIN10TOAST = False  # Set to False to use MessageBox instead

class EnhancedClipboardMonitor:
    """
    Monitors the clipboard for new images, extracts medication information,
    displays administration instructions, and provides a system tray icon for user control.
    """
    
    def __init__(self):
        """Initialize the clipboard monitor."""
        self.logger = logging.getLogger("EnhancedClipboardMonitor")
        self.logger.info("Initializing enhanced clipboard monitor...")
        
        self.last_image = None
        self.running = False
        self.monitor_thread = None
        self.tray_icon = None
        
        # Initialize text analyzer
        self.analyzer = ImprovedTextAnalyzer()
        
        # Initialize OCR processor
        self.ocr = OCRProcessor()
        
        self.logger.info("Enhanced clipboard monitor initialized")
    
    def start(self):
        """Start monitoring the clipboard."""
        if self.running:
            self.logger.warning("Clipboard monitor already running")
            return
        
        self.logger.info("Starting clipboard monitor...")
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_clipboard)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        self.logger.info("Clipboard monitor started")
    
    def stop(self):
        """Stop monitoring the clipboard."""
        if not self.running:
            self.logger.warning("Clipboard monitor not running")
            return
        
        self.logger.info("Stopping clipboard monitor...")
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5.0)
        self.logger.info("Clipboard monitor stopped")
    
    def _monitor_clipboard(self):
        """Monitor the clipboard for new images."""
        self.logger.info("Clipboard monitoring thread started")
        
        while self.running:
            try:
                # Check if there's an image in the clipboard
                if self._is_image_in_clipboard():
                    self.logger.info("Image detected in clipboard")
                    
                    # Get the image from the clipboard
                    image = ImageGrab.grabclipboard()
                    
                    # Check if it's a new image
                    if self._is_new_image(image):
                        self.logger.info("New image detected")
                        
                        # Process the image
                        self._process_image(image)
                        
                        # Add a timestamp to clipboard for debugging
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        debug_text = f"Image processed at {timestamp}"
                        self.logger.info(debug_text)
                    else:
                        self.logger.debug("Image already processed")
                
                # Sleep for a bit
                time.sleep(POLL_INTERVAL)
            
            except Exception as e:
                self.logger.error(f"Error monitoring clipboard: {e}")
                time.sleep(POLL_INTERVAL)
    
    def _is_image_in_clipboard(self):
        """Check if there's an image in the clipboard."""
        try:
            # Try to grab the clipboard contents
            clipboard_content = ImageGrab.grabclipboard()
            
            # Check if it's an image
            return isinstance(clipboard_content, Image.Image)
        
        except Exception as e:
            self.logger.error(f"Error checking clipboard for image: {e}")
            return False
    
    def _is_new_image(self, image):
        """Check if the image is new (different from the last processed image)."""
        if not image or not self.last_image:
            return True
        
        # Convert images to bytes for comparison
        try:
            image_bytes = io.BytesIO()
            image.save(image_bytes, format='PNG')
            image_data = image_bytes.getvalue()
            
            last_image_bytes = io.BytesIO()
            self.last_image.save(last_image_bytes, format='PNG')
            last_image_data = last_image_bytes.getvalue()
            
            # Compare the image data
            return image_data != last_image_data
        
        except Exception as e:
            self.logger.error(f"Error comparing images: {e}")
            return True
    
    def _process_image(self, image):
        """Process an image from the clipboard."""
        self.logger.info("Processing clipboard image...")
        
        try:
            # Save the image as the last processed image
            self.last_image = image
            
            # Save the image for debugging
            debug_image_path = "debug_clipboard_image.png"
            image.save(debug_image_path)
            self.logger.info(f"Image saved to {debug_image_path} for debugging")
            
            # Extract text from the image
            self.logger.info("Extracting text from image...")
            extracted_text = self.ocr.extract_text(image)
            
            if not extracted_text:
                self.logger.warning("No text extracted from image")
                self.show_dialog("OCR Failed", "No text could be extracted from the image.")
                return
            
            # Save the extracted text for debugging
            with open(EXTRACTED_TEXT_FILE, "w", encoding="utf-8") as f:
                f.write(extracted_text)
            
            self.logger.info(f"Text extracted and saved to {EXTRACTED_TEXT_FILE}")
            
            # Analyze the text
            self.logger.info("Analyzing extracted text...")
            extracted_info = self.analyzer.analyze_text(extracted_text)
            
            if not extracted_info:
                self.logger.warning("No information extracted from text")
                self.show_dialog("Analysis Failed", "No medication information could be extracted from the text.")
                return
            
            self.logger.info(f"Extracted information: {extracted_info}")
            
            # Get medication name
            if 'medication' in extracted_info:
                medication = extracted_info['medication']
                self.logger.info(f"Medication found: {medication}")
                
                # Look up medication in database
                self.logger.info(f"Looking up administration instructions for: {medication}")
                results = lookup_medication(medication, silent=True)
                
                if results and len(results) > 0:
                    admin_instructions = results[0]['administration']
                    self.logger.info(f"Administration instructions: {admin_instructions}")
                    
                    # Show notification
                    self.show_dialog("Medication Found", admin_instructions)
                    
                    # Copy to clipboard
                    self.copy_to_clipboard(admin_instructions)
                    
                    # Save the results
                    self._save_results(extracted_info, admin_instructions)
                else:
                    self.logger.warning(f"No administration instructions found for {medication}")
                    self.show_dialog("Medication Not Found", f"No administration instructions found for {medication}")
            else:
                self.logger.warning("No medication name found in extracted text")
                self.show_dialog("Analysis Result", "No medication name found in the extracted text.")
        
        except Exception as e:
            self.logger.error(f"Error processing image: {e}")
            self.show_dialog("Processing Error", f"Error processing image: {str(e)}")
    
    def show_dialog(self, title, message):
        """Show a dialog message."""
        self.logger.info(f"Showing dialog: {title} - {message}")
        try:
            win32api.MessageBox(0, message, title, win32con.MB_OK)
            self.logger.info("Dialog shown successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error showing dialog: {e}")
            return False
    
    def copy_to_clipboard(self, text):
        """Copy text to clipboard and verify it was copied."""
        self.logger.info(f"Copying to clipboard: {text}")
        
        try:
            # Try to copy the text to clipboard
            pyperclip.copy(text)
            
            # Verify the text was copied correctly
            clipboard_content = pyperclip.paste()
            if clipboard_content == text:
                self.logger.info("Text successfully copied to clipboard")
                return True
            else:
                self.logger.warning("Failed to copy text to clipboard")
                return False
        
        except Exception as e:
            self.logger.error(f"Error copying to clipboard: {e}")
            return False
    
    def _save_results(self, extracted_info, admin_instructions):
        """Save the results to a file."""
        self.logger.info(f"Saving results to {OUTPUT_FILE}")
        
        try:
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                f.write("Extracted Information:\n\n")
                f.write(f"HPR-nr: {extracted_info.get('hpr_number', 'Not found')}\n")
                f.write(f"Prescriber: {extracted_info.get('prescriber', 'Not found')}\n")
                f.write(f"Medication: {extracted_info.get('medication', 'Not found')}\n\n")
                f.write(f"Administration Instructions from Database:\n{admin_instructions}\n\n")
                f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            self.logger.info(f"Results saved to {OUTPUT_FILE}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error saving results: {e}")
            return False
    
    def create_tray_icon_image(self):
        """Create an image for the system tray icon."""
        # Create a blank image with a white background
        image = Image.new("RGB", (64, 64), "white")
        draw = ImageDraw.Draw(image)
        # Draw a simple shape (e.g., a red square)
        draw.rectangle([16, 16, 48, 48], fill="red")
        return image
    
    def create_tray_icon(self):
        """Create and run the system tray icon."""
        def on_quit(icon, item):
            self.stop()
            icon.stop()
        
        def on_toggle_monitor(icon, item):
            if self.running:
                self.stop()
            else:
                self.start()
            # Update menu text
            icon.menu = create_menu()
        
        def create_menu():
            monitor_text = "Stop Monitoring" if self.running else "Start Monitoring"
            return pystray.Menu(
                pystray.MenuItem(monitor_text, on_toggle_monitor),
                pystray.MenuItem("Quit", on_quit)
            )
        
        try:
            icon_image = self.create_tray_icon_image()
            self.tray_icon = pystray.Icon("MedicalTextExtractor")
            self.tray_icon.icon = icon_image
            self.tray_icon.menu = create_menu()
            self.tray_icon.title = "Medical Text Extractor"
            self.logger.info("Starting system tray icon...")
            self.tray_icon.run()
            self.logger.info("System tray icon stopped")
        except Exception as e:
            self.logger.error(f"Error with system tray icon: {e}")
    
    def run(self):
        """Run the enhanced clipboard monitor with system tray icon."""
        # Start the clipboard monitor in a separate thread
        self.start()
        
        # Create and run the system tray icon in the main thread
        self.create_tray_icon()
        
        # When the tray icon exits, make sure to stop the monitor
        self.stop()

def main():
    """Main function to start the enhanced clipboard monitor."""
    logger.info("Starting enhanced clipboard monitor service...")
    
    # Create monitor
    monitor = EnhancedClipboardMonitor()
    
    try:
        # Run the monitor with system tray icon
        monitor.run()
    
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    
    except Exception as e:
        logger.error(f"Error in main thread: {e}")
    
    finally:
        # Stop monitoring
        monitor.stop()
        logger.info("Enhanced clipboard monitor service stopped")

if __name__ == "__main__":
    main()
