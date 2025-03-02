#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Comprehensive debugging script for the clipboard monitor
"""

import os
import sys
import time
import logging
from PIL import ImageGrab, Image

# Import the tesseract path configuration
try:
    from tesseract_path import *
except ImportError:
    pass

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('debug.log')
    ]
)
logger = logging.getLogger("Debug")

# Import the components
try:
    from improved_text_analyzer import ImprovedTextAnalyzer
    from ocr_processor import OCRProcessor
    from lookup_medication import lookup_medication
    
    components_imported = True
except ImportError as e:
    logger.error(f"Error importing components: {e}")
    components_imported = False

def test_clipboard_image_detection():
    """Test if an image can be detected in the clipboard."""
    logger.info("Testing clipboard image detection...")
    
    try:
        # Try to grab the clipboard contents
        clipboard_content = ImageGrab.grabclipboard()
        
        # Log the type of content
        logger.info(f"Clipboard content type: {type(clipboard_content)}")
        
        # Check if it's an image
        if isinstance(clipboard_content, Image.Image):
            logger.info("Image detected in clipboard!")
            
            # Save the image for debugging
            clipboard_content.save("debug_clipboard_image.png")
            logger.info("Image saved as debug_clipboard_image.png")
            
            return clipboard_content
        else:
            logger.warning("No image detected in clipboard")
            logger.debug(f"Clipboard content: {clipboard_content}")
            return None
    
    except Exception as e:
        logger.error(f"Error checking clipboard for image: {e}")
        return None

def test_ocr(image):
    """Test OCR on the image."""
    logger.info("Testing OCR...")
    
    try:
        # Create OCR processor
        ocr = OCRProcessor()
        
        # Extract text from the image
        logger.info("Extracting text from image...")
        extracted_text = ocr.extract_text(image)
        
        if not extracted_text:
            logger.warning("No text extracted from image")
            return None
        
        # Save the extracted text for debugging
        with open("debug_extracted_text.txt", "w", encoding="utf-8") as f:
            f.write(extracted_text)
        
        logger.info(f"Text extracted and saved to debug_extracted_text.txt")
        logger.debug(f"Extracted text: {extracted_text}")
        
        return extracted_text
    
    except Exception as e:
        logger.error(f"Error in OCR: {e}")
        return None

def test_text_analysis(text):
    """Test text analysis on the extracted text."""
    logger.info("Testing text analysis...")
    
    try:
        # Create text analyzer
        analyzer = ImprovedTextAnalyzer()
        
        # Analyze the text
        logger.info("Analyzing extracted text...")
        extracted_info = analyzer.analyze_text(text)
        
        if not extracted_info:
            logger.warning("No information extracted from text")
            return None
        
        logger.info(f"Extracted information: {extracted_info}")
        
        return extracted_info
    
    except Exception as e:
        logger.error(f"Error in text analysis: {e}")
        return None

def test_medication_lookup(medication):
    """Test medication lookup."""
    logger.info(f"Testing medication lookup for: {medication}")
    
    try:
        # Look up medication in database
        results = lookup_medication(medication, silent=True)
        
        if results and len(results) > 0:
            admin_instructions = results[0]['administration']
            logger.info(f"Administration instructions: {admin_instructions}")
            return admin_instructions
        else:
            logger.warning(f"No administration instructions found for {medication}")
            return None
    
    except Exception as e:
        logger.error(f"Error in medication lookup: {e}")
        return None

def test_file_creation():
    """Test file creation."""
    logger.info("Testing file creation...")
    
    try:
        # Try to create a test file
        with open("debug_test_file.txt", "w", encoding="utf-8") as f:
            f.write("Test file creation")
        
        # Check if the file was created
        if os.path.exists("debug_test_file.txt"):
            logger.info("File creation successful")
            return True
        else:
            logger.warning("File creation failed")
            return False
    
    except Exception as e:
        logger.error(f"Error in file creation: {e}")
        return False

def main():
    """Main function to run all tests."""
    logger.info("Starting comprehensive debug...")
    
    # Test clipboard image detection
    image = test_clipboard_image_detection()
    if not image:
        logger.error("Clipboard image detection failed")
        return
    
    # Test OCR
    text = test_ocr(image)
    if not text:
        logger.error("OCR failed")
        return
    
    # Test text analysis
    extracted_info = test_text_analysis(text)
    if not extracted_info:
        logger.error("Text analysis failed")
        return
    
    # Test medication lookup
    if 'medication' in extracted_info:
        medication = extracted_info['medication']
        admin_instructions = test_medication_lookup(medication)
        if not admin_instructions:
            logger.error("Medication lookup failed")
            return
    else:
        logger.error("No medication found in extracted information")
        return
    
    # Test file creation
    if not test_file_creation():
        logger.error("File creation failed")
        return
    
    # All tests passed
    logger.info("All tests passed!")
    
    # Create a simulated clipboard_results.txt
    try:
        with open("debug_clipboard_results.txt", "w", encoding="utf-8") as f:
            f.write("Extracted Information:\n\n")
            f.write(f"HPR-nr: {extracted_info.get('hpr_number', 'Not found')}\n")
            f.write(f"Prescriber: {extracted_info.get('prescriber', 'Not found')}\n")
            f.write(f"Medication: {extracted_info.get('medication', 'Not found')}\n\n")
            f.write(f"Administration Instructions from Database:\n{admin_instructions}\n\n")
            f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        logger.info("Debug results saved to debug_clipboard_results.txt")
    
    except Exception as e:
        logger.error(f"Error creating debug results: {e}")

if __name__ == "__main__":
    if not components_imported:
        logger.error("Cannot run tests due to import errors")
        sys.exit(1)
    
    main()
