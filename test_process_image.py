#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script to directly process an image file
"""

import os
import sys
import time
from PIL import Image
import pyperclip

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ocr_processor import OCRProcessor
from improved_text_analyzer import ImprovedTextAnalyzer
from lookup_medication import lookup_medication

def process_image_file(image_path):
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
        else:
            print("No medication name could be extracted")
    
    except Exception as e:
        print(f"Error processing image: {e}")

if __name__ == "__main__":
    # Check if an image path was provided
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        # Look for sample images in the current directory
        sample_images = [f for f in os.listdir('.') if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
        
        if sample_images:
            image_path = sample_images[0]
            print(f"No image specified, using first image found: {image_path}")
        else:
            print("No image specified and no images found in the current directory.")
            print("Usage: python test_process_image.py [image_path]")
            sys.exit(1)
    
    # Process the image
    process_image_file(image_path)
