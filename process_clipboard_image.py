#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to process an image from the clipboard, extract medication information,
and display the results.
"""

import os
import sys
import logging
import io
import re
from PIL import ImageGrab, Image
from improved_text_analyzer import ImprovedTextAnalyzer
from ocr_processor import OCRProcessor
from lookup_medication import lookup_medication

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("clipboard_process.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def get_image_from_clipboard():
    """Get an image from the clipboard."""
    try:
        # Grab image from clipboard
        image = ImageGrab.grabclipboard()
        
        if image is None:
            print("No image found in clipboard.")
            return None
        
        if isinstance(image, Image.Image):
            print("Image found in clipboard.")
            return image
        elif isinstance(image, list):
            # Handle case where clipboard contains a list of file paths
            if image and os.path.isfile(image[0]):
                try:
                    return Image.open(image[0])
                except Exception as e:
                    print(f"Error opening image file: {e}")
                    return None
        
        print("Clipboard content is not a valid image.")
        return None
    except Exception as e:
        print(f"Error accessing clipboard: {e}")
        return None

def process_clipboard_image():
    """Process an image from the clipboard and extract medication information."""
    print("=" * 80)
    print("PROCESSING IMAGE FROM CLIPBOARD")
    print("=" * 80)
    
    # Get image from clipboard
    image = get_image_from_clipboard()
    
    if image is None:
        print("Failed to get a valid image from clipboard.")
        return
    
    # Save the image temporarily for debugging
    temp_image_path = "clipboard_image.png"
    image.save(temp_image_path)
    print(f"Saved clipboard image to {temp_image_path}")
    
    # Initialize OCR processor
    ocr_processor = OCRProcessor()
    
    # Extract text from image
    print("\nExtracting text from image...")
    extracted_text = ocr_processor.extract_text(image)
    
    if not extracted_text:
        print("No text could be extracted from the image.")
        return
    
    # Save extracted text for debugging
    with open("extracted_text.txt", "w", encoding="utf-8") as f:
        f.write(extracted_text)
    print(f"Saved extracted text to extracted_text.txt")
    
    # Try to directly extract HPR and medication from the text
    hpr_match = re.search(r'HPR:?\s*(\d+)', extracted_text, re.IGNORECASE)
    med_match = re.search(r'Legemiddel:?\s*([^\n]+)', extracted_text, re.IGNORECASE)
    
    hpr_number = hpr_match.group(1) if hpr_match else "Not found"
    
    # If no Legemiddel pattern is found, try to get the second line as medication
    if med_match:
        medication = med_match.group(1).strip()
    else:
        # Split by lines and try to find medication name
        lines = [line.strip() for line in extracted_text.split('\n') if line.strip()]
        if len(lines) >= 2 and not lines[1].startswith('HPR'):
            medication = lines[1]
        else:
            medication = "Not found"
    
    # Initialize improved text analyzer
    analyzer = ImprovedTextAnalyzer()
    
    # Analyze the text
    print("\nAnalyzing extracted text...")
    extracted_info = analyzer.analyze_text(extracted_text)
    
    # Override with direct matches if they exist
    if hpr_match:
        extracted_info['hpr_number'] = hpr_number
    if medication != "Not found":
        extracted_info['medication'] = medication
    
    # Print extracted information
    print("\nExtracted Information:")
    print("=" * 80)
    print(f"HPR-nr: {extracted_info.get('hpr_number', 'Not found')}")
    print(f"Prescriber: {extracted_info.get('prescriber', 'Not found')}")
    print(f"Medication: {extracted_info.get('medication', 'Not found')}")
    print("=" * 80)
    
    # Save results to file
    with open("clipboard_results.txt", "w", encoding="utf-8") as f:
        f.write("Extracted Information:\n\n")
        f.write(f"HPR-nr: {extracted_info.get('hpr_number', 'Not found')}\n")
        f.write(f"Prescriber: {extracted_info.get('prescriber', 'Not found')}\n")
        f.write(f"Medication: {extracted_info.get('medication', 'Not found')}\n")
    
    # If medication was found, look it up in the database
    medication = extracted_info.get('medication')
    if medication and medication != "Not found" and not medication.startswith("HPR"):
        print("\nLooking up administration instructions for", medication)
        print("=" * 80)
        results = lookup_medication(medication)
        
        # Append administration instructions to the results file
        with open("clipboard_results.txt", "a", encoding="utf-8") as f:
            if results:
                f.write(f"\nAdministration Instructions from Database:\n")
                f.write(f"{results[0]['administration']}\n")
            else:
                f.write(f"\nNo administration instructions found in database for {medication}\n")
    
    print(f"\nResults saved to clipboard_results.txt")
    
    return extracted_info

if __name__ == "__main__":
    process_clipboard_image()
    
    print("\nOperation completed. See clipboard_process.log for detailed logging information.")
