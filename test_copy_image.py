#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script to copy an image to the clipboard
"""

import os
import sys
import time
from PIL import Image, ImageGrab

# Path to the test image
IMAGE_PATH = "clipboard_image.png"

def copy_image_to_clipboard():
    """Copy an image to the clipboard."""
    print(f"Copying image to clipboard: {IMAGE_PATH}")
    
    try:
        # Open the image
        if not os.path.exists(IMAGE_PATH):
            print(f"Error: Image file not found: {IMAGE_PATH}")
            return False
        
        image = Image.open(IMAGE_PATH)
        
        # Copy to clipboard (Windows only)
        import win32clipboard
        from io import BytesIO
        
        output = BytesIO()
        image.convert("RGB").save(output, "BMP")
        data = output.getvalue()[14:]  # The file header offset of BMP is 14 bytes
        output.close()
        
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
        win32clipboard.CloseClipboard()
        
        print("Image copied to clipboard successfully!")
        return True
    
    except Exception as e:
        print(f"Error copying image to clipboard: {e}")
        return False

if __name__ == "__main__":
    # Copy the image to the clipboard
    copy_image_to_clipboard()
    
    # Wait a bit for the clipboard monitor to detect the image
    print("Waiting for clipboard monitor to detect the image...")
    time.sleep(5)
    
    # Check if the clipboard_results.txt file was created
    if os.path.exists("clipboard_results.txt"):
        print("Success! Clipboard monitor detected the image and created clipboard_results.txt")
        
        # Print the contents of the file
        with open("clipboard_results.txt", "r", encoding="utf-8") as f:
            print("\nContents of clipboard_results.txt:")
            print(f.read())
    else:
        print("Error: Clipboard monitor did not create clipboard_results.txt")
        print("Check if the clipboard monitor service is running correctly.")
