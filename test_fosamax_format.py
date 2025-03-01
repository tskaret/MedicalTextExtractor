#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script to analyze the Fosamax administration instructions
using the TextAnalyzer component.
"""

import logging
from text_analyzer import TextAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("fosamax_test.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def test_fosamax_format():
    """Test the TextAnalyzer with Fosamax administration instructions."""
    # Initialize text analyzer
    analyzer = TextAnalyzer()
    
    # Fosamax text to analyze
    fosamax_text = """Fosamax

Tabletten skal tas straks pasienten står opp om morgenen, sammen med et fullt glass vann på fastende mage, minst 1/2 time før inntak av annen drikke, mat eller andre legemidler. For å lette transporten til magen, og derved redusere risikoen for lokal og øsofageal irritasjon​/​bivirkning, skal pasienten sitte oppreist eller stå inntil dagens første måltid er inntatt (dvs. minst 1/2 time etter tablettinntak). Tabletten skal ikke tas ved sengetid eller før en står opp. Tabletten skal svelges hel. Skal ikke tygges, knuses eller oppløses i munnen.

doctor 10017852, Torgny Skaret"""
    
    # Analyze the text
    print("Analyzing Fosamax text...")
    results = analyzer.get_structured_data(fosamax_text)
    
    # Extract values from results
    prescriber = None
    medication = None
    administration = None
    
    if 'prescriber' in results:
        if isinstance(results['prescriber'], dict):
            prescriber = results['prescriber'].get('value')
        else:
            prescriber = results['prescriber']
    
    if 'medication' in results:
        if isinstance(results['medication'], dict):
            medication = results['medication'].get('value')
        else:
            medication = results['medication']
    
    if 'administration' in results:
        if isinstance(results['administration'], dict):
            administration = results['administration'].get('value')
        else:
            administration = results['administration']
    
    # Print results
    print("\nEXTRACTED INFORMATION:")
    print(f"Prescriber: {prescriber or 'Not found'}")
    print(f"Medication: {medication or 'Not found'}")
    print(f"Administration: {administration or 'Not found'}")
    
    # Print confidence scores if available
    prescriber_conf = results.get('prescriber', {}).get('confidence', 0) if isinstance(results.get('prescriber'), dict) else 0
    medication_conf = results.get('medication', {}).get('confidence', 0) if isinstance(results.get('medication'), dict) else 0
    admin_conf = results.get('administration', {}).get('confidence', 0) if isinstance(results.get('administration'), dict) else 0
    
    print("\nCONFIDENCE SCORES:")
    print(f"Prescriber: {prescriber_conf:.2f}")
    print(f"Medication: {medication_conf:.2f}")
    print(f"Administration: {admin_conf:.2f}")
    
    # Evaluate extraction success
    print("\nEXTRACTION EVALUATION:")
    print(f"Prescriber extraction: {'Success' if prescriber else 'Failed'}")
    print(f"Medication extraction: {'Success' if medication else 'Failed'}")
    print(f"Administration extraction: {'Success' if administration else 'Failed'}")
    
    # Log results
    logger.info("Fosamax text analysis completed")
    if prescriber:
        logger.info(f"Extracted prescriber: {prescriber}")
    else:
        logger.warning("Failed to extract prescriber")
    
    if medication:
        logger.info(f"Extracted medication: {medication}")
    else:
        logger.warning("Failed to extract medication")
    
    if administration:
        logger.info(f"Extracted administration: {administration}")
    else:
        logger.warning("Failed to extract administration")
    
    return results

if __name__ == "__main__":
    print("=" * 80)
    print("TESTING FOSAMAX FORMAT")
    print("=" * 80)
    
    results = test_fosamax_format()
    
    print("\nTest completed. See fosamax_test.log for detailed logging information.")
