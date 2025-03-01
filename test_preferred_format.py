#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script for the improved text analyzer with the user's preferred format.
"""

import json
import logging
from improved_text_analyzer import ImprovedTextAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("preferred_format_test.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def test_fosamax_format():
    """Test the improved analyzer with Fosamax format."""
    # Initialize improved text analyzer
    analyzer = ImprovedTextAnalyzer()
    
    # Fosamax text to analyze
    fosamax_text = """Fosamax

Tabletten skal tas straks pasienten står opp om morgenen, sammen med et fullt glass vann på fastende mage, minst 1/2 time før inntak av annen drikke, mat eller andre legemidler. For å lette transporten til magen, og derved redusere risikoen for lokal og øsofageal irritasjon​/​bivirkning, skal pasienten sitte oppreist eller stå inntil dagens første måltid er inntatt (dvs. minst 1/2 time etter tablettinntak). Tabletten skal ikke tas ved sengetid eller før en står opp. Tabletten skal svelges hel. Skal ikke tygges, knuses eller oppløses i munnen.

doctor 10017852, Torgny Skaret"""
    
    # Analyze the text
    print("Analyzing Fosamax text with improved analyzer...")
    results = analyzer.analyze_text(fosamax_text)
    
    # Print results in the preferred format
    print("\nExtracted Information:")
    print(f"HPR-nr:{results.get('hpr_number', 'Not found')}")
    print(f"Prescriber: {results.get('prescriber', 'Not found')}")
    print(f"Medication: {results.get('medication', 'Not found')}")
    print(f"Administration: {results.get('administration', 'Not found')}")
    
    # Write results to a file
    with open('preferred_format_results.txt', 'w', encoding='utf-8') as f:
        f.write("Extracted Information:\n\n")
        f.write(f"HPR-nr:{results.get('hpr_number', 'Not found')}\n")
        f.write(f"Prescriber: {results.get('prescriber', 'Not found')}\n")
        f.write(f"Medication: {results.get('medication', 'Not found')}\n")
        f.write(f"Administration: {results.get('administration', 'Not found')}\n")
    
    print("\nResults written to preferred_format_results.txt")
    
    # Log results
    logger.info("Fosamax text analysis completed with improved analyzer")
    logger.info(f"Extracted HPR number: {results.get('hpr_number', 'Not found')}")
    logger.info(f"Extracted prescriber: {results.get('prescriber', 'Not found')}")
    logger.info(f"Extracted medication: {results.get('medication', 'Not found')}")
    logger.info(f"Extracted administration: {results.get('administration', 'Not found')}")
    
    return results

def test_with_explicit_format():
    """Test the analyzer with explicitly formatted text."""
    # Initialize improved text analyzer
    analyzer = ImprovedTextAnalyzer()
    
    # Text with explicit format
    explicit_text = """HPR-nr:10017852
Prescriber: Torgny Skaret
Medication: Fosamax
Administration: Tabletten skal tas straks pasienten står opp om morgenen, sammen med et fullt glass vann på fastende mage, minst 1/2 time før inntak av annen drikke, mat eller andre legemidler. for å lette transporten til magen, og derved redusere risikoen for lokal og øsofageal irritasjon​/​bivirkning, skal pasienten sitte oppreist eller stå inntil dagens første måltid er inntatt (dvs. minst 1/2 time etter tablettinntak). tabletten skal ikke tas ved sengetid eller før en står opp. tabletten skal svelges hel. skal ikke tygges, knuses eller oppløses i munnen."""
    
    # Analyze the text
    print("\n\nAnalyzing explicitly formatted text...")
    results = analyzer.analyze_text(explicit_text)
    
    # Print results in the preferred format
    print("\nExtracted Information:")
    print(f"HPR-nr:{results.get('hpr_number', 'Not found')}")
    print(f"Prescriber: {results.get('prescriber', 'Not found')}")
    print(f"Medication: {results.get('medication', 'Not found')}")
    print(f"Administration: {results.get('administration', 'Not found')}")
    
    # Write results to a file
    with open('explicit_format_results.txt', 'w', encoding='utf-8') as f:
        f.write("Extracted Information:\n\n")
        f.write(f"HPR-nr:{results.get('hpr_number', 'Not found')}\n")
        f.write(f"Prescriber: {results.get('prescriber', 'Not found')}\n")
        f.write(f"Medication: {results.get('medication', 'Not found')}\n")
        f.write(f"Administration: {results.get('administration', 'Not found')}\n")
    
    print("\nResults written to explicit_format_results.txt")
    
    # Log results
    logger.info("Explicit format text analysis completed")
    logger.info(f"Extracted HPR number: {results.get('hpr_number', 'Not found')}")
    logger.info(f"Extracted prescriber: {results.get('prescriber', 'Not found')}")
    logger.info(f"Extracted medication: {results.get('medication', 'Not found')}")
    logger.info(f"Extracted administration: {results.get('administration', 'Not found')}")
    
    return results

if __name__ == "__main__":
    print("=" * 80)
    print("TESTING IMPROVED TEXT ANALYZER WITH PREFERRED FORMAT")
    print("=" * 80)
    
    # Test with Fosamax format
    results_fosamax = test_fosamax_format()
    
    # Test with explicit format
    results_explicit = test_with_explicit_format()
    
    print("\nTest completed. See preferred_format_test.log for detailed logging information.")
