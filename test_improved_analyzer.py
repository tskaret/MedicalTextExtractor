#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script for the improved text analyzer.
"""

import json
import logging
from improved_text_analyzer import ImprovedTextAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("improved_analyzer_test.log"),
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
    
    # Write results to a file
    with open('improved_analyzer_results.txt', 'w', encoding='utf-8') as f:
        f.write("Raw Results Dictionary:\n")
        f.write(json.dumps(results, indent=2, ensure_ascii=False))
        
        f.write("\n\nExtracted Information:\n")
        f.write(f"Prescriber: {results.get('prescriber', 'Not found')}\n")
        f.write(f"Medication: {results.get('medication', 'Not found')}\n")
        f.write(f"Administration: {results.get('administration', 'Not found')}\n")
    
    print("Results written to improved_analyzer_results.txt")
    
    # Log results
    logger.info("Fosamax text analysis completed with improved analyzer")
    logger.info(f"Extracted prescriber: {results.get('prescriber', 'Not found')}")
    logger.info(f"Extracted medication: {results.get('medication', 'Not found')}")
    logger.info(f"Extracted administration: {results.get('administration', 'Not found')}")
    
    return results

if __name__ == "__main__":
    print("=" * 80)
    print("TESTING IMPROVED TEXT ANALYZER WITH FOSAMAX FORMAT")
    print("=" * 80)
    
    results = test_fosamax_format()
    
    print("\nTest completed. See improved_analyzer_test.log for detailed logging information.")
