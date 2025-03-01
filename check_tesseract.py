#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Check Tesseract OCR installation
"""

import os
import sys
import subprocess
import platform

def check_tesseract():
    """Check if Tesseract OCR is installed and configured correctly."""
    print("Checking Tesseract OCR installation...")
    
    # Check if pytesseract is installed
    try:
        import pytesseract
        print("✓ pytesseract is installed")
    except ImportError:
        print("✗ pytesseract is not installed")
        print("  Run: pip install pytesseract")
        return False
    
    # Check Tesseract path
    tesseract_path = pytesseract.pytesseract.tesseract_cmd
    print(f"Current Tesseract path: {tesseract_path}")
    
    # Check if the path exists
    if os.path.exists(tesseract_path):
        print(f"✓ Tesseract executable found at: {tesseract_path}")
    else:
        print(f"✗ Tesseract executable not found at: {tesseract_path}")
        
        # Try to find tesseract in common locations
        common_locations = []
        
        if platform.system() == 'Windows':
            program_files = os.environ.get('PROGRAMFILES', 'C:\\Program Files')
            program_files_x86 = os.environ.get('PROGRAMFILES(X86)', 'C:\\Program Files (x86)')
            
            common_locations = [
                os.path.join(program_files, 'Tesseract-OCR', 'tesseract.exe'),
                os.path.join(program_files_x86, 'Tesseract-OCR', 'tesseract.exe'),
                'C:\\Program Files\\Tesseract-OCR\\tesseract.exe',
                'C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe',
            ]
        else:  # Linux/Mac
            common_locations = [
                '/usr/bin/tesseract',
                '/usr/local/bin/tesseract',
            ]
        
        # Check common locations
        for location in common_locations:
            if os.path.exists(location):
                print(f"✓ Tesseract found at alternative location: {location}")
                print(f"  Set this path in your code or environment variable.")
                return True
        
        print("✗ Tesseract not found in common locations")
        print("  Please install Tesseract OCR:")
        if platform.system() == 'Windows':
            print("  1. Download from: https://github.com/UB-Mannheim/tesseract/wiki")
            print("  2. Install and add to PATH")
        else:
            print("  1. Run: sudo apt-get install tesseract-ocr")
        
        return False
    
    # Try to run tesseract version command
    try:
        version_output = subprocess.check_output([tesseract_path, '--version'], stderr=subprocess.STDOUT, universal_newlines=True)
        print(f"✓ Tesseract version: {version_output.split()[1]}")
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"✗ Error running tesseract: {e}")
        return False
    
    # Check for language data
    try:
        langs_output = subprocess.check_output([tesseract_path, '--list-langs'], stderr=subprocess.STDOUT, universal_newlines=True)
        langs = langs_output.strip().split('\n')[1:]  # Skip the first line which is a header
        print(f"✓ Available languages: {', '.join(langs)}")
        
        if 'eng' not in langs:
            print("✗ English language data not found")
            print("  Download language data from: https://github.com/tesseract-ocr/tessdata")
            return False
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"✗ Error checking languages: {e}")
        return False
    
    print("\nTesseract OCR is properly installed and configured!")
    return True

def fix_tesseract_path():
    """Try to fix the Tesseract path in the environment."""
    import pytesseract
    
    # Common Tesseract installation paths on Windows
    common_paths = [
        'C:\\Program Files\\Tesseract-OCR\\tesseract.exe',
        'C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe',
    ]
    
    # Check if any of these paths exist
    for path in common_paths:
        if os.path.exists(path):
            print(f"Setting Tesseract path to: {path}")
            pytesseract.pytesseract.tesseract_cmd = path
            
            # Create a file to set this path in future runs
            with open('tesseract_path.py', 'w') as f:
                f.write(f"""# Set Tesseract path
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'{path}'
""")
            
            print("Created tesseract_path.py to set the path in future runs")
            print("Import this file at the beginning of your scripts")
            return True
    
    print("Could not find Tesseract in common locations")
    print("Please install Tesseract OCR from: https://github.com/UB-Mannheim/tesseract/wiki")
    return False

if __name__ == "__main__":
    if not check_tesseract():
        print("\nAttempting to fix Tesseract path...")
        fix_tesseract_path()
