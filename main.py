#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Medical Text Extractor - Main Application

This script integrates all components of the Medical Text Extractor application,
providing functionality to detect screenshots, extract medication information
using OCR, store it in a database, and copy it to the clipboard.
"""

import os
import sys
import time
import logging
import threading
from pathlib import Path

# Import application components
try:
    from screenshot_monitor import ScreenshotMonitor
    from ocr_processor import OCRProcessor
    from text_analyzer import TextAnalyzer
    from database.db_manager import DatabaseManager
    from clipboard_manager import ClipboardManager
except ImportError as e:
    print(f"Error importing components: {e}")
    print("Make sure all required modules are installed and in the correct location.")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("medical_text_extractor.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class MedicalTextExtractor:
    """Main application class that integrates all components."""
    
    def __init__(self, db_path=None):
        """Initialize the application and its components."""
        logger.info("Initializing Medical Text Extractor application")
        
        # Set default database path if not provided
        if db_path is None:
            db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                "database", "medical_data.db")
        
        # Ensure database directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Initialize components
        try:
            self.db_manager = DatabaseManager(db_path)
            self.ocr_processor = OCRProcessor()
            self.text_analyzer = TextAnalyzer()
            self.clipboard_manager = ClipboardManager(self.db_manager)
            
            # Initialize screenshot monitor with a callback
            self.screenshot_monitor = ScreenshotMonitor(
                on_screenshot=self._process_screenshot
            )
            
            self._monitoring = False
            self._monitor_thread = None
            
            logger.info("All components initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            raise
    
    def _process_screenshot(self, image):
        """Process a screenshot image when detected."""
        try:
            logger.info("Processing new screenshot")
            # Extract text using OCR
            text = self.ocr_processor.extract_text(image)
            
            if not text:
                logger.warning("No text extracted from screenshot")
                return
            
            # Analyze text for medication information
            medication_info = self.text_analyzer.analyze(text)
            
            if medication_info:
                # Store information in database
                med_id = self.db_manager.store_medication_info(medication_info)
                logger.info(f"Stored medication information with ID: {med_id}")
                
                # Notify user
                print("\nDetected medication information:")
                print(f"Prescriber: {medication_info.get('prescriber', 'Unknown')}")
                print(f"Medication: {medication_info.get('medication', 'Unknown')}")
                print(f"Instructions: {medication_info.get('instructions', 'Unknown')}")
                print("Use 'copy <medication_name>' to copy instructions to clipboard\n")
            else:
                logger.info("No medication information found in the text")
        except Exception as e:
            logger.error(f"Error processing screenshot: {e}")
    
    def start_monitoring(self):
        """Start monitoring for screenshots in a separate thread."""
        if self._monitoring:
            print("Screenshot monitoring is already running")
            return
        
        logger.info("Starting screenshot monitoring")
        self._monitoring = True
        self._monitor_thread = threading.Thread(
            target=self._run_monitoring,
            daemon=True
        )
        self._monitor_thread.start()
        print("Screenshot monitoring started")
    
    def _run_monitoring(self):
        """Run the screenshot monitoring loop."""
        try:
            self.screenshot_monitor.start()
            while self._monitoring:
                time.sleep(0.1)  # Small sleep to prevent CPU hogging
            self.screenshot_monitor.stop()
        except Exception as e:
            logger.error(f"Error in monitoring thread: {e}")
            self._monitoring = False
    
    def stop_monitoring(self):
        """Stop monitoring for screenshots."""
        if not self._monitoring:
            print("Screenshot monitoring is not running")
            return
        
        logger.info("Stopping screenshot monitoring")
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=2.0)
        print("Screenshot monitoring stopped")
    
    def search_medication(self, term):
        """Search for medication information in the database."""
        try:
            results = self.db_manager.search_medications(term)
            
            if not results:
                print(f"No results found for '{term}'")
                return []
            
            print(f"\nFound {len(results)} result(s) for '{term}':")
            for i, result in enumerate(results, 1):
                print(f"{i}. Medication: {result.get('medication', 'Unknown')}")
                print(f"   Prescriber: {result.get('prescriber', 'Unknown')}")
                print(f"   Instructions: {result.get('instructions', 'Unknown')}")
                print(f"   Date: {result.get('date', 'Unknown')}")
                print()
            
            return results
        except Exception as e:
            logger.error(f"Error searching for medication: {e}")
            print(f"Error searching for medication: {e}")
            return []
    
    def copy_to_clipboard(self, medication_name):
        """Copy medication instructions to clipboard."""
        try:
            success = self.clipboard_manager.copy_instructions(medication_name)
            
            if success:
                print(f"Instructions for '{medication_name}' copied to clipboard")
            else:
                print(f"No instructions found for '{medication_name}'")
            
            return success
        except Exception as e:
            logger.error(f"Error copying to clipboard: {e}")
            print(f"Error copying to clipboard: {e}")
            return False
    
    def minimize_to_tray(self):
        """Minimize application to system tray."""
        # This would require a GUI framework like PyQt or wxPython
        # For this CLI version, we'll just print a message
        print("Application is running in the background. Use 'exit' to quit.")
        logger.info("Application minimized to background")
    
    def shutdown(self):
        """Clean shutdown of the application."""
        logger.info("Shutting down Medical Text Extractor")
        self.stop_monitoring()
        # Close any open resources
        self.db_manager.close()
        print("Application shut down successfully")


def print_help():
    """Print help information."""
    print("\nMedical Text Extractor - Command Help")
    print("====================================")
    print("start       - Start monitoring for screenshots")
    print("stop        - Stop monitoring for screenshots")
    print("status      - Show monitoring status")
    print("search <term> - Search for medication by name")
    print("copy <name> - Copy instructions for medication to clipboard")
    print("minimize    - Run in background (conceptual in CLI)")
    print("help        - Show this help message")
    print("exit        - Exit the application")
    print("")


def main():
    """Main entry point for the application."""
    try:
        # Create application instance
        app = MedicalTextExtractor()
        
        print("\nMedical Text Extractor")
        print("=====================")
        print("Type 'help' for a list of commands.")
        
        # Simple command loop
        while True:
            try:
                command = input("\n> ").strip().lower()
                
                if command == "exit":
                    app.shutdown()
                    break
                
                elif command == "help":
                    print_help()
                
                elif command == "start":
                    app.start_monitoring()
                
                elif command == "stop":
                    app.stop_monitoring()
                
                elif command == "status":
                    if app._monitoring:
                        print("Screenshot monitoring is active")
                    else:
                        print("Screenshot monitoring is inactive")
                
                elif command.startswith("search "):
                    term = command[7:].strip()
                    if term:
                        app.search_medication(term)
                    else:
                        print("Please provide a search term")
                
                elif command.startswith("copy "):
                    medication = command[5:].strip()
                    if medication:
                        app.copy_to_clipboard(medication)
                    else:
                        print("Please provide a medication name")
                
                elif command == "minimize":
                    app.minimize_to_tray()
                
                else:
                    print(f"Unknown command: {command}")
                    print("Type 'help' for a list of commands")
            
            except KeyboardInterrupt:
                print("\nUse 'exit' to quit the application")
            
            except Exception as e:
                logger.error(f"Error processing command: {e}")
                print(f"Error: {e}")
    
    except Exception as e:
        logger.error(f"Application error: {e}")
        print(f"Error starting application: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

