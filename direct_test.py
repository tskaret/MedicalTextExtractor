#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Direct test for clipboard monitoring functionality
"""

import os
import sys
import time
import ctypes
import pyperclip
from PIL import Image, ImageDraw, ImageFont

# Import the tesseract path configuration
try:
    from tesseract_path import *
except ImportError:
    pass

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ocr_processor import OCRProcessor
from improved_text_analyzer import ImprovedTextAnalyzer
from lookup_medication import lookup_medication

def create_test_image(filename="test_medication.png"):
    """Create a test image with medication information."""
    # Create a white image
    width, height = 800, 600
    image = Image.new('RGB', (width, height), color='white')
    
    # Get a drawing context
    draw = ImageDraw.Draw(image)
    
    # Try to use a font
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except IOError:
        font = ImageFont.load_default()
    
    # Add text to the image
    text = """
    HPR: 10017852
    
    Fosamax
    
    Dosering: 1 tablett ukentlig
    """
    
    # Draw the text
    draw.text((50, 50), text, fill='black', font=font)
    
    # Save the image
    image.save(filename)
    print(f"Test image created: {filename}")
    
    return os.path.abspath(filename)

def show_message_box(title, message):
    """Show a Windows message box."""
    print(f"Showing message box: {title} - {message}")
    ctypes.windll.user32.MessageBoxW(0, message, title, 0)

def process_image(image_path):
    """Process an image file and extract medication information."""
    print(f"Processing image: {image_path}")
    
    # Check if file exists
    if not os.path.exists(image_path):
        print(f"Error: File {image_path} does not exist")
        return
    
    try:
        # Open the image
        image = Image.open(image_path)
        print(f"Image opened successfully: {image.size}")
        
        # Extract text from image
        ocr_processor = OCRProcessor()
        print("Extracting text from image...")
        extracted_text = ocr_processor.extract_text(image)
        
        if not extracted_text:
            print("No text could be extracted from the image")
            return
        
        print("\nExtracted text:")
        print("-" * 40)
        print(extracted_text)
        print("-" * 40)
        
        # Save extracted text for debugging
        with open("test_extracted_text.txt", "w", encoding="utf-8") as f:
            f.write(extracted_text)
        
        # Analyze the text
        analyzer = ImprovedTextAnalyzer()
        print("\nAnalyzing extracted text...")
        extracted_info = analyzer.analyze_text(extracted_text)
        
        if not extracted_info:
            print("No information could be extracted from the text")
            return
        
        print("\nExtracted information:")
        print("-" * 40)
        for key, value in extracted_info.items():
            print(f"{key}: {value}")
        print("-" * 40)
        
        # Get medication name
        if 'medication' in extracted_info:
            medication = extracted_info['medication']
            print(f"\nLooking up administration instructions for: {medication}")
            
            # Look up medication in database
            results = lookup_medication(medication, silent=False)
            
            if results and len(results) > 0:
                admin_instructions = results[0]['administration']
                print("\nAdministration instructions:")
                print("-" * 40)
                print(admin_instructions)
                print("-" * 40)
                
                # Copy to clipboard
                print("\nCopying administration instructions to clipboard...")
                pyperclip.copy(admin_instructions)
                print("Instructions copied to clipboard. Try pasting them now.")
                
                # Show message box
                show_message_box("Medication Found", admin_instructions)
                
                # Save the results
                with open("test_results.txt", "w", encoding="utf-8") as f:
                    f.write("Extracted Information:\n\n")
                    f.write(f"HPR-nr: {extracted_info.get('hpr_number', 'Not found')}\n")
                    f.write(f"Prescriber: {extracted_info.get('prescriber', 'Not found')}\n")
                    f.write(f"Medication: {medication}\n\n")
                    f.write(f"Administration Instructions from Database:\n{admin_instructions}\n\n")
                    f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            else:
                print("No administration instructions found for this medication")
                show_message_box("Medication Not Found", f"No administration instructions found for {medication}")
        else:
            print("No medication name could be extracted")
            show_message_box("Error", "No medication name could be extracted from the image")
    
    except Exception as e:
        print(f"Error processing image: {e}")
        show_message_box("Error", f"Error processing image: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("DIRECT TEST FOR CLIPBOARD MONITORING")
    print("=" * 60)
    
    # Create a test image
    image_path = create_test_image()
    
    # Process the image
    process_image(image_path)
    
    print("\nTest completed!")
