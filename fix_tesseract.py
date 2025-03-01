#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Fix Tesseract OCR configuration
"""

import os
import sys
import subprocess
import shutil
import ctypes
import platform

def is_admin():
    """Check if the script is running with administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def show_message_box(title, message):
    """Show a Windows message box."""
    ctypes.windll.user32.MessageBoxW(0, message, title, 0)

def find_tesseract_path():
    """Find the Tesseract installation path."""
    # Common Tesseract installation paths on Windows
    common_paths = [
        'C:\\Program Files\\Tesseract-OCR',
        'C:\\Program Files (x86)\\Tesseract-OCR',
    ]
    
    # Check if any of these paths exist
    for path in common_paths:
        exe_path = os.path.join(path, 'tesseract.exe')
        if os.path.exists(exe_path):
            return path
    
    return None

def check_language_data(tesseract_path):
    """Check if language data is installed."""
    tessdata_path = os.path.join(tesseract_path, 'tessdata')
    
    if not os.path.exists(tessdata_path):
        return False
    
    # Check for required language files
    required_langs = ['eng.traineddata', 'nor.traineddata']
    missing_langs = []
    
    for lang in required_langs:
        if not os.path.exists(os.path.join(tessdata_path, lang)):
            missing_langs.append(lang)
    
    return missing_langs

def download_language_data(tesseract_path, missing_langs):
    """Download missing language data."""
    tessdata_path = os.path.join(tesseract_path, 'tessdata')
    
    # Create tessdata directory if it doesn't exist
    if not os.path.exists(tessdata_path):
        os.makedirs(tessdata_path)
    
    # Base URL for language data
    base_url = "https://github.com/tesseract-ocr/tessdata/raw/main/"
    
    print(f"Downloading missing language data to {tessdata_path}...")
    
    for lang in missing_langs:
        url = base_url + lang
        output_file = os.path.join(tessdata_path, lang)
        
        print(f"Downloading {lang}...")
        
        try:
            # Use PowerShell to download the file
            ps_command = f"Invoke-WebRequest -Uri '{url}' -OutFile '{output_file}'"
            subprocess.run(["powershell", "-Command", ps_command], check=True)
            print(f"Successfully downloaded {lang}")
        except subprocess.CalledProcessError as e:
            print(f"Error downloading {lang}: {e}")
            return False
    
    return True

def main():
    """Main function."""
    print("=" * 60)
    print("TESSERACT OCR CONFIGURATION FIX")
    print("=" * 60)
    
    # Check if running as administrator
    if not is_admin():
        print("This script should be run as administrator.")
        show_message_box("Administrator Required", 
                         "This script needs to be run as administrator to fix Tesseract OCR configuration.")
        return
    
    # Find Tesseract installation path
    tesseract_path = find_tesseract_path()
    
    if not tesseract_path:
        print("Tesseract OCR not found.")
        show_message_box("Tesseract Not Found", 
                         "Tesseract OCR installation not found. Please install Tesseract OCR first.")
        return
    
    print(f"Tesseract OCR found at: {tesseract_path}")
    
    # Check language data
    missing_langs = check_language_data(tesseract_path)
    
    if not missing_langs:
        print("All required language data is installed.")
        show_message_box("Language Data OK", 
                         "All required language data is already installed.")
        return
    
    print(f"Missing language data: {', '.join(missing_langs)}")
    
    # Download missing language data
    success = download_language_data(tesseract_path, missing_langs)
    
    if success:
        print("Successfully fixed Tesseract OCR configuration.")
        show_message_box("Fix Successful", 
                         "Successfully fixed Tesseract OCR configuration. The clipboard monitor should now work correctly.")
    else:
        print("Failed to fix Tesseract OCR configuration.")
        show_message_box("Fix Failed", 
                         "Failed to fix Tesseract OCR configuration. Please download the language data manually.")

if __name__ == "__main__":
    main()
