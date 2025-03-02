#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Debug script to test clipboard image detection
"""

import os
import sys
import time
from PIL import ImageGrab, Image
import io

def is_image_in_clipboard():
    """Check if there's an image in the clipboard."""
    try:
        # Try to grab the clipboard contents
        clipboard_content = ImageGrab.grabclipboard()
        
        # Print the type of content
        print(f"Clipboard content type: {type(clipboard_content)}")
        
        # Check if it's an image
        if isinstance(clipboard_content, Image.Image):
            print("Image detected in clipboard!")
            
            # Save the image for debugging
            clipboard_content.save("debug_clipboard_image.png")
            print("Image saved as debug_clipboard_image.png")
            
            return True
        else:
            print("No image detected in clipboard")
            print(f"Clipboard content: {clipboard_content}")
            return False
    
    except Exception as e:
        print(f"Error checking clipboard for image: {e}")
        return False

if __name__ == "__main__":
    print("Debugging clipboard image detection...")
    
    # Check if there's an image in the clipboard
    is_image = is_image_in_clipboard()
    
    print(f"\nResult: {'Image found' if is_image else 'No image found'} in clipboard")
