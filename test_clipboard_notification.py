#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script to directly test the notification functionality
"""

import os
import sys
import time
import subprocess
import pyperclip
from PIL import Image

# Import the tesseract path configuration
try:
    from tesseract_path import *
except ImportError:
    pass

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def show_notification(title, message):
    """Show a notification using PowerShell."""
    print(f"Showing notification: {title} - {message}")
    
    # Escape single quotes in the message
    message = message.replace("'", "''")
    title = title.replace("'", "''")
    
    # PowerShell command to show a notification using BurntToast module
    ps_command = f"""
    $title = '{title}'
    $message = '{message}'
    
    # Try using BurntToast module if available
    if (Get-Module -ListAvailable -Name BurntToast) {{
        Import-Module BurntToast
        New-BurntToastNotification -Text $title, $message
    }} else {{
        # Fallback to simple MessageBox
        Add-Type -AssemblyName System.Windows.Forms
        [System.Windows.Forms.MessageBox]::Show($message, $title)
    }}
    """
    
    try:
        # Run the PowerShell command
        subprocess.run(["powershell", "-Command", ps_command], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error showing PowerShell notification: {e}")
        
        # Try a simpler approach
        try:
            simple_command = f'Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.MessageBox]::Show("{message}", "{title}")'
            subprocess.run(["powershell", "-Command", simple_command], check=True)
            return True
        except subprocess.CalledProcessError as e2:
            print(f"Error showing simple notification: {e2}")
            return False

def copy_to_clipboard(text):
    """Copy text to clipboard and verify it was copied."""
    print(f"Copying to clipboard: {text}")
    
    # Try to copy the text to clipboard
    try:
        pyperclip.copy(text)
        
        # Verify the text was copied correctly
        clipboard_content = pyperclip.paste()
        if clipboard_content == text:
            print("Text successfully copied to clipboard!")
            return True
        else:
            print("Failed to copy text to clipboard!")
            return False
    except Exception as e:
        print(f"Error copying to clipboard: {e}")
        return False

def test_notification_and_clipboard():
    """Test the notification and clipboard functionality."""
    # Test data
    title = "Medication Found"
    message = "1 tablett ukentlig"
    
    # Test notification
    print("\n--- Testing Notification ---")
    notification_result = show_notification(title, message)
    
    # Test clipboard
    print("\n--- Testing Clipboard ---")
    clipboard_result = copy_to_clipboard(message)
    
    # Print results
    print("\n--- Test Results ---")
    print(f"Notification: {'SUCCESS' if notification_result else 'FAILED'}")
    print(f"Clipboard: {'SUCCESS' if clipboard_result else 'FAILED'}")

if __name__ == "__main__":
    test_notification_and_clipboard()
