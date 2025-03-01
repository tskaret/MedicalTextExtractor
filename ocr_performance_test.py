#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
OCR Performance Test for Medical Text Extractor

This script tests the end-to-end performance of the OCR and text analysis pipeline
by processing sample images, extracting text with OCR, and then analyzing the extracted
text to identify medication information.

The script can use both real images (if available) and simulated OCR output.
"""

import os
import sys
import logging
import time
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# Import application components
try:
    from ocr_processor import OCRProcessor
    from text_analyzer import TextAnalyzer
except ImportError as e:
    print(f"Error importing components: {e}")
    print("Make sure all required modules are installed and in the correct location.")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("ocr_performance_test.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Define sample texts for image generation
SAMPLE_TEXTS = [
    # Standard prescription format
    """
    RESEPT
    
    Rekvirent: Dr. Erik Hansen
    Legesenter: Oslo Medisinske Senter
    
    Pasient: Andersen, Marte
    Fødselsdato: 15.04.1985
    
    Legemiddel: Paracetamol 500mg tabletter
    Styrke: 500mg
    Antall: 100 tabletter
    
    Dosering: 1-2 tabletter hver 4-6 time ved behov
    Maksimal døgndose: 8 tabletter (4000mg)
    """,
    
    # Hospital format
    """
    UNIVERSITETSSYKEHUSET NORD-NORGE
    Avdeling: Medisinsk
    
    ORDINASJONSKORT
    
    Pasient: Hansen, Nils (12.05.1965)
    
    Ordinert av: Overlege Dr. Kristin Svendsen
    
    MEDIKAMENT: Warfarin Orion 2,5 mg
    
    ADMINISTRASJON:
    Mandag: 1 tablett
    Tirsdag: 1/2 tablett
    Onsdag: 1 tablett
    Torsdag: 1/2 tablett
    Fredag: 1 tablett
    Lørdag: 1/2 tablett
    Søndag: 1/2 tablett
    """,
    
    # Pharmacy label format
    """
    APOTEK 1 STORTORGET
    Tlf: 815 22 333
    
    PARACET 500 mg tabletter
    100 stk
    
    Til: Jensen, Lise
    
    DOSERING:
    1-2 tabletter inntil 3-4 ganger daglig ved behov.
    Maksimalt 8 tabletter per døgn.
    """
]

def create_test_image(text, width=800, height=600, filename="test_image.png"):
    """Create a test image with the given text."""
    # Create a white background image
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    # Try to use a standard font
    try:
        font = ImageFont.truetype("arial.ttf", 16)
    except IOError:
        # Fall back to default font
        font = ImageFont.load_default()
    
    # Draw text on the image
    draw.text((20, 20), text, fill='black', font=font)
    
    # Save the image
    image.save(filename)
    logger.info(f"Created test image: {filename}")
    
    return filename

def simulate_ocr_errors(text, error_rate=0.05):
    """Simulate OCR errors by randomly replacing characters."""
    if not text:
        return text
    
    # Define common OCR error substitutions
    ocr_errors = {
        'e': '€', 'o': '0', 'l': '1', 'i': '!', 's': '$',
        'a': '@', 't': '+', 'b': '6', 'g': '9', 'z': '2'
    }
    
    # Convert text to list of characters for easier manipulation
    chars = list(text)
    
    # Randomly introduce errors
    for i in range(len(chars)):
        if chars[i] in ocr_errors and np.random.random() < error_rate:
            chars[i] = ocr_errors[chars[i]]
    
    return ''.join(chars)

def test_with_generated_images():
    """Test the OCR and text analysis pipeline with generated images."""
    logger.info("Starting tests with generated images")
    
    # Initialize components
    ocr = OCRProcessor()
    analyzer = TextAnalyzer()
    
    results = []
    
    # Create test directory if it doesn't exist
    test_img_dir = Path("test_images")
    test_img_dir.mkdir(exist_ok=True)
    
    # Process each sample text
    for i, sample_text in enumerate(SAMPLE_TEXTS):
        test_name = f"Sample {i+1}"
        logger.info(f"Testing with {test_name}")
        
        # Create a test image
        image_path = str(test_img_dir / f"test_image_{i+1}.png")
        create_test_image(sample_text, filename=image_path)
        
        # Extract text with OCR
        start_time = time.time()
        extracted_text = ocr.extract_text(image_path)
        ocr_time = time.time() - start_time
        
        if not extracted_text:
            logger.warning(f"No text extracted from {image_path}")
            continue
        
        # Analyze the extracted text
        start_time = time.time()
        analysis = analyzer.get_structured_data(extracted_text)
        analysis_time = time.time() - start_time
        
        # Get the extracted information
        prescriber = analysis.get('prescriber', {}).get('value') if isinstance(analysis.get('prescriber'), dict) else analysis.get('prescriber')
        medication = analysis.get('medication', {}).get('value') if isinstance(analysis.get('medication'), dict) else analysis.get('medication')
        administration = analysis.get('administration', {}).get('value') if isinstance(analysis.get('administration'), dict) else analysis.get('administration')
        
        # Store results
        results.append({
            'test_name': test_name,
            'image_path': image_path,
            'original_text': sample_text,
            'extracted_text': extracted_text,
            'prescriber': prescriber,
            'medication': medication,
            'administration': administration,
            'ocr_time': ocr_time,
            'analysis_time': analysis_time
        })
        
        # Print results
        print(f"\n{'=' * 80}")
        print(f"TEST: {test_name}")
        print(f"{'=' * 80}")
        print(f"Image: {image_path}")
        print(f"OCR Time: {ocr_time:.2f} seconds")
        print(f"Analysis Time: {analysis_time:.2f} seconds")
        print("\nEXTRACTED TEXT (sample):")
        print(extracted_text[:200] + "..." if len(extracted_text) > 200 else extracted_text)
        print("\nEXTRACTED INFORMATION:")
        print(f"Prescriber: {prescriber or 'Not found'}")
        print(f"Medication: {medication or 'Not found'}")
        print(f"Administration: {administration or 'Not found'}")
    
    return results

def test_with_simulated_ocr():
    """Test the text analyzer with simulated OCR output."""
    logger.info("Starting tests with simulated OCR output")
    
    # Initialize analyzer
    analyzer = TextAnalyzer()
    
    results = []
    
    # Process each sample text with different error rates
    error_rates = [0.0, 0.05, 0.1, 0.2]
    
    for i, sample_text in enumerate(SAMPLE_TEXTS):
        for error_rate in error_rates:
            test_name = f"Sample {i+1} (Error Rate: {error_rate:.2f})"
            logger.info(f"Testing with {test_name}")
            
            # Simulate OCR output with errors
            simulated_ocr = simulate_ocr_errors(sample_text, error_rate)
            
            # Analyze the simulated OCR text
            start_time = time.time()
            analysis = analyzer.get_structured_data(simulated_ocr)
            analysis_time = time.time() - start_time
            
            # Get the extracted information
            prescriber = analysis.get('prescriber', {}).get('value') if isinstance(analysis.get('prescriber'), dict) else analysis.get('prescriber')
            medication = analysis.get('medication', {}).get('value') if isinstance(analysis.get('medication'), dict) else analysis.get('medication')
            administration = analysis.get('administration', {}).get('value') if isinstance(analysis.get('administration'), dict) else analysis.get('administration')
            
            # Store results
            results.append({
                'test_name': test_name,
                'error_rate': error_rate,
                'original_text': sample_text,
                'simulated_ocr': simulated_ocr,
                'prescriber': prescriber,
                'medication': medication,
                'administration': administration,
                'analysis_time': analysis_time
            })
            
            # Print results
            print(f"\n{'=' * 80}")
            print(f"TEST: {test_name}")
            print(f"{'=' * 80}")
            print(f"Error Rate: {error_rate:.2f}")
            print(f"Analysis Time: {analysis_time:.2f} seconds")
            print("\nSIMULATED OCR TEXT (sample):")
            print(simulated_ocr[:200] + "..." if len(simulated_ocr) > 200 else simulated_ocr)
            print("\nEXTRACTED INFORMATION:")
            print(f"Prescriber: {prescriber or 'Not found'}")
            print(f"Medication: {medication or 'Not found'}")
            print(f"Administration: {administration or 'Not found'}")
    
    return results

def main():
    """Main function to run the OCR performance tests."""
    print("MEDICAL TEXT EXTRACTOR - OCR PERFORMANCE TEST")
    print("=" * 80)
    
    all_results = {
        'generated_images': [],
        'simulated_ocr': []
    }
    
    # Test with generated images
    print("\nTESTING WITH GENERATED IMAGES:")
    try:
        all_results['generated_images'] = test_with_generated_images()
    except Exception as e:
        logger.error(f"Error in generated images test: {e}")
        print(f"Error in generated images test: {e}")
    
    # Test with simulated OCR
    print("\nTESTING WITH SIMULATED OCR OUTPUT:")
    try:
        all_results['simulated_ocr'] = test_with_simulated_ocr()
    except Exception as e:
        logger.error(f"Error in simulated OCR test: {e}")
        print(f"Error in simulated OCR test: {e}")
    
    # Save results to JSON file
    try:
        with open('ocr_test_results.json', 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2)
        print("\nDetailed results saved to ocr_test_results.json")
    except Exception as e:
        logger.error(f"Error saving results to JSON: {e}")
    
    # Print summary
    print("\nTEST SUMMARY:")
    print(f"Generated Image Tests: {len(all_results['generated_images'])}")
    print(f"Simulated OCR Tests: {len(all_results['simulated_ocr'])}")
    print("\nSee ocr_performance_test.log for detailed logging information")

if __name__ == "__main__":
    main()
