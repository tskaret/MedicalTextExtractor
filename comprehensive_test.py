#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Comprehensive test for the improved text analyzer.
Tests various input formats and verifies the extraction results.
"""

import os
import logging
from improved_text_analyzer import ImprovedTextAnalyzer
from database.db_manager import DatabaseManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("comprehensive_test.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def test_analyzer(text, description):
    """Test the improved text analyzer with the given text."""
    print(f"\n{'=' * 40}")
    print(f"TEST: {description}")
    print(f"{'=' * 40}")
    
    # Initialize analyzer
    analyzer = ImprovedTextAnalyzer()
    
    # Analyze text
    result = analyzer.analyze_text(text)
    
    # Print results
    print("\nExtracted Information:")
    print(f"HPR-nr: {result.get('hpr_number', 'Not found')}")
    print(f"Prescriber: {result.get('prescriber', 'Not found')}")
    print(f"Medication: {result.get('medication', 'Not found')}")
    print(f"Administration: {result.get('administration', 'Not found')}")
    
    # Write results to file
    filename = f"{description.lower().replace(' ', '_')}_results.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("Extracted Information:\n\n")
        f.write(f"HPR-nr:{result.get('hpr_number', 'Not found')}\n")
        f.write(f"Prescriber: {result.get('prescriber', 'Not found')}\n")
        f.write(f"Medication: {result.get('medication', 'Not found')}\n")
        f.write(f"Administration: {result.get('administration', 'Not found')}\n")
    
    print(f"\nResults written to {filename}")
    
    return result

def test_database_storage(text, description):
    """Test storing the extracted information in the database."""
    print(f"\n{'=' * 40}")
    print(f"DATABASE TEST: {description}")
    print(f"{'=' * 40}")
    
    # Set database path
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                          "database", "medical_data.db")
    
    # Initialize database manager and analyzer
    db_manager = DatabaseManager(db_path)
    analyzer = ImprovedTextAnalyzer()
    
    # Analyze text
    extracted_info = analyzer.analyze_text(text)
    
    # Prepare medication information for database
    medication_info = {
        'medication': extracted_info.get('medication'),
        'prescriber': f"{extracted_info.get('prescriber')} ({extracted_info.get('hpr_number')})" if extracted_info.get('hpr_number') else extracted_info.get('prescriber'),
        'administration': extracted_info.get('administration'),
        'original_text': text
    }
    
    # Store in database
    med_id = db_manager.store_medication_info(medication_info)
    
    if med_id > 0:
        print(f"\nSuccessfully added {medication_info['medication']} to the database with ID: {med_id}")
        
        # Verify storage
        medication = db_manager.get_medication_by_id(med_id)
        
        if medication:
            print("\nVerification - Medication found in database:")
            print(f"ID: {medication['id']}")
            print(f"Medication: {medication['medication']}")
            print(f"Prescriber: {medication['prescriber']}")
            print(f"Administration: {medication['administration'][:100]}...")  # Show first 100 chars
            print(f"Date: {medication['date']}")
        else:
            print(f"Medication with ID {med_id} not found in database")
    else:
        print("\nFailed to add medication to the database")
    
    # Close database connection
    db_manager.close()
    
    return med_id

if __name__ == "__main__":
    print("=" * 80)
    print("COMPREHENSIVE TEST FOR IMPROVED TEXT ANALYZER")
    print("=" * 80)
    
    # Test 1: Standard format
    standard_text = """Fosamax

Tabletten skal tas straks pasienten står opp om morgenen, sammen med et fullt glass vann på fastende mage, minst 1/2 time før inntak av annen drikke, mat eller andre legemidler. For å lette transporten til magen, og derved redusere risikoen for lokal og øsofageal irritasjon​/​bivirkning, skal pasienten sitte oppreist eller stå inntil dagens første måltid er inntatt (dvs. minst 1/2 time etter tablettinntak). Tabletten skal ikke tas ved sengetid eller før en står opp. Tabletten skal svelges hel. Skal ikke tygges, knuses eller oppløses i munnen.

doctor 10017852, Torgny Skaret"""
    
    test_analyzer(standard_text, "Standard Format")
    
    # Test 2: Explicit format
    explicit_text = """HPR-nr:10017852
Prescriber: Torgny Skaret
Medication: Fosamax
Administration: Tabletten skal tas straks pasienten står opp om morgenen, sammen med et fullt glass vann på fastende mage, minst 1/2 time før inntak av annen drikke, mat eller andre legemidler. for å lette transporten til magen, og derved redusere risikoen for lokal og øsofageal irritasjon​/​bivirkning, skal pasienten sitte oppreist eller stå inntil dagens første måltid er inntatt (dvs. minst 1/2 time etter tablettinntak). tabletten skal ikke tas ved sengetid eller før en står opp. tabletten skal svelges hel. skal ikke tygges, knuses eller oppløses i munnen."""
    
    test_analyzer(explicit_text, "Explicit Format")
    
    # Test 3: Different medication
    different_med_text = """Lipitor

Ta én tablett daglig. Kan tas når som helst på dagen, med eller uten mat.

doctor 10017852, Torgny Skaret"""
    
    test_analyzer(different_med_text, "Different Medication")
    
    # Test 4: Different doctor
    different_doctor_text = """Fosamax

Tabletten skal tas straks pasienten står opp om morgenen, sammen med et fullt glass vann på fastende mage, minst 1/2 time før inntak av annen drikke, mat eller andre legemidler.

doctor 98765432, Jane Doe"""
    
    test_analyzer(different_doctor_text, "Different Doctor")
    
    # Test 5: Database storage test
    test_database_storage(standard_text, "Standard Format Database Storage")
    test_database_storage(explicit_text, "Explicit Format Database Storage")
    
    print("\nTest completed. See comprehensive_test.log for detailed logging information.")
