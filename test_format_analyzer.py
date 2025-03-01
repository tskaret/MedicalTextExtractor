#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script for evaluating the TextAnalyzer with various medication information formats.
This script tests how well the TextAnalyzer handles different formats, missing information,
and OCR errors in medication information.
"""

import os
import sys
import logging
from pathlib import Path
from text_analyzer import TextAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("format_test_results.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def load_test_data(file_path):
    """Load test data from a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        logger.error(f"Error loading test data from {file_path}: {e}")
        return None

def print_analysis_results(format_name, text, results):
    """Print the analysis results in a formatted way."""
    print(f"\n{'=' * 80}")
    print(f"FORMAT: {format_name}")
    print(f"{'=' * 80}")
    
    # Print original text (truncated if too long)
    max_text_length = 300
    if len(text) > max_text_length:
        display_text = text[:max_text_length] + "..."
    else:
        display_text = text
    print(f"ORIGINAL TEXT:\n{display_text}\n")
    
    # Print extracted information
    print("EXTRACTED INFORMATION:")
    print(f"Prescriber: {results.get('prescriber', 'Not found')}")
    print(f"Medication: {results.get('medication', 'Not found')}")
    print(f"Administration: {results.get('administration', 'Not found')}")
    
    # Print confidence scores if available
    if 'prescriber' in results and isinstance(results['prescriber'], dict):
        print("\nCONFIDENCE SCORES:")
        print(f"Prescriber: {results['prescriber'].get('confidence', 'N/A'):.2f}")
        print(f"Medication: {results['medication'].get('confidence', 'N/A'):.2f}")
        print(f"Administration: {results['administration'].get('confidence', 'N/A'):.2f}")

def main():
    """Main function to run the format tests."""
    # Initialize the text analyzer
    analyzer = TextAnalyzer()
    
    # Define test data files
    test_dir = Path("test_data")
    test_files = {
        "Standard Format": test_dir / "standard_format.txt",
        "Alternative Format": test_dir / "alternative_format.txt",
        "Different Separators": test_dir / "different_separators.txt",
        "Missing Information": test_dir / "missing_info_format.txt",
        "OCR Errors": test_dir / "ocr_errors_format.txt"
    }
    
    # Process each test file
    for format_name, file_path in test_files.items():
        logger.info(f"Testing {format_name} from {file_path}")
        
        # Load test data
        text = load_test_data(file_path)
        if not text:
            logger.error(f"Failed to load test data for {format_name}")
            continue
        
        # Analyze text
        try:
            results = analyzer.get_structured_data(text)
            print_analysis_results(format_name, text, results)
            
            # Log results
            logger.info(f"Analysis completed for {format_name}")
            if results.get('prescriber', {}).get('value'):
                logger.info(f"Found prescriber: {results['prescriber']['value']}")
            if results.get('medication', {}).get('value'):
                logger.info(f"Found medication: {results['medication']['value']}")
            if results.get('administration', {}).get('value'):
                logger.info(f"Found administration: {results['administration']['value']}")
        except Exception as e:
            logger.error(f"Error analyzing {format_name}: {e}")
            print(f"Error analyzing {format_name}: {e}")
    
    print("\nTEST SUMMARY:")
    print(f"Tested {len(test_files)} different medication information formats")
    print("See format_test_results.log for detailed logging information")

if __name__ == "__main__":
    main()
