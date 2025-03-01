#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Clipboard Monitor - Automatically detects images in clipboard, extracts medication information,
and displays administration instructions in a toast notification.
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
from PIL import ImageGrab, Image

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
logger = logging.getLogger("ClipboardMonitor")

# Constants
POLL_INTERVAL = 1.0  # seconds
OUTPUT_FILE = "clipboard_results.txt"
EXTRACTED_TEXT_FILE = "extracted_text.txt"
USE_WIN10TOAST = False  # Set to False to use MessageBox instead

class ClipboardMonitor:
    """
    Monitors the clipboard for new images, extracts medication information,
    and displays toast notifications with administration instructions.
    """
    
    def __init__(self):
        """Initialize the clipboard monitor."""
        self.logger = logging.getLogger("ClipboardMonitor")
        self.logger.info("Initializing clipboard monitor...")
        
        self.last_image = None
        self.running = False
        self.monitor_thread = None
        
        # Initialize text analyzer
        self.analyzer = ImprovedTextAnalyzer()
        
        # Initialize OCR processor
        self.ocr = OCRProcessor()
        
        self.logger.info("Clipboard monitor initialized")
    
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
            
            # Extract text from the image
            self.logger.info("Extracting text from image...")
            extracted_text = self.ocr.extract_text(image)
            
            if not extracted_text:
                self.logger.warning("No text extracted from image")
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
                    self.show_notification("Medication Found", admin_instructions)
                    
                    # Copy to clipboard
                    self.copy_to_clipboard(admin_instructions)
                    
                    # Save the results
                    self._save_results(extracted_info, admin_instructions)
                else:
                    self.logger.warning(f"No administration instructions found for {medication}")
            else:
                self.logger.warning("No medication name found in extracted text")
        
        except Exception as e:
            self.logger.error(f"Error processing image: {e}")
    
    def show_notification(self, title, message):
        """Show a notification with the given title and message."""
        self.logger.info(f"Showing notification: {title} - {message}")
        
        try:
            # Use Windows MessageBox for notifications
            # This will create a standard Windows dialog box that requires user interaction
            ctypes.windll.user32.MessageBoxW(0, message, title, 0)
            self.logger.info("Notification shown successfully using MessageBox")
            return True
        except Exception as e:
            self.logger.error(f"Error showing notification: {e}")
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

def main():
    """Main function to start the clipboard monitor."""
    logger.info("Starting clipboard monitor service...")
    
    # Create monitor
    monitor = ClipboardMonitor()
    
    try:
        # Start monitoring
        monitor.start()
        
        # Keep the main thread alive
        while True:
            time.sleep(1)
    
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    
    except Exception as e:
        logger.error(f"Error in main thread: {e}")
    
    finally:
        # Stop monitoring
        monitor.stop()
        logger.info("Clipboard monitor service stopped")

if __name__ == "__main__":
    main()
