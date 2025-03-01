#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to add a medication to the database using the improved text analyzer.
This can be used for testing or to pre-populate the database with known medications.
"""

import os
import sys
import logging
from database.db_manager import DatabaseManager
from improved_text_analyzer import ImprovedTextAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("add_medication_improved.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def add_medication_to_database(text):
    """Add medication information to the database using the improved text analyzer."""
    # Set database path
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                          "database", "medical_data.db")
    
    # Initialize database manager
    db_manager = DatabaseManager(db_path)
    
    # Initialize improved text analyzer
    analyzer = ImprovedTextAnalyzer()
    
    # Analyze the text
    print("Analyzing medication text...")
    extracted_info = analyzer.analyze_text(text)
    
    # Print extracted information
    print("\nExtracted Information:")
    print(f"HPR-nr: {extracted_info.get('hpr_number', 'Not found')}")
    print(f"Prescriber: {extracted_info.get('prescriber', 'Not found')}")
    print(f"Medication: {extracted_info.get('medication', 'Not found')}")
    print(f"Administration: {extracted_info.get('administration', 'Not found')}")
    
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
        logger.info(f"Added {medication_info['medication']} to database with ID: {med_id}")
    else:
        print("\nFailed to add medication to the database")
        logger.error("Failed to add medication to database")
    
    # Close database connection
    db_manager.close()
    
    return med_id

def verify_medication_in_database(med_id):
    """Verify that the medication was added to the database."""
    # Set database path
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                          "database", "medical_data.db")
    
    # Initialize database manager
    db_manager = DatabaseManager(db_path)
    
    # Get medication by ID
    medication = db_manager.get_medication_by_id(med_id)
    
    if medication:
        print("\nVerification - Medication found in database:")
        print(f"ID: {medication['id']}")
        print(f"Medication: {medication['medication']}")
        print(f"Prescriber: {medication['prescriber']}")
        print(f"Administration: {medication['administration'][:100]}...")  # Show first 100 chars
        print(f"Date: {medication['date']}")
        
        logger.info(f"Verified medication with ID {med_id} is in database")
    else:
        print(f"Medication with ID {med_id} not found in database")
        logger.error(f"Medication with ID {med_id} not found in database")
    
    # Close database connection
    db_manager.close()

if __name__ == "__main__":
    print("=" * 80)
    print("ADDING MEDICATION TO DATABASE USING IMPROVED TEXT ANALYZER")
    print("=" * 80)
    
    # Fosamax text
    fosamax_text = """Fosamax

Tabletten skal tas straks pasienten står opp om morgenen, sammen med et fullt glass vann på fastende mage, minst 1/2 time før inntak av annen drikke, mat eller andre legemidler. For å lette transporten til magen, og derved redusere risikoen for lokal og øsofageal irritasjon​/​bivirkning, skal pasienten sitte oppreist eller stå inntil dagens første måltid er inntatt (dvs. minst 1/2 time etter tablettinntak). Tabletten skal ikke tas ved sengetid eller før en står opp. Tabletten skal svelges hel. Skal ikke tygges, knuses eller oppløses i munnen.

doctor 10017852, Torgny Skaret"""
    
    # Add Fosamax to database
    print("Adding Fosamax to the database...")
    med_id = add_medication_to_database(fosamax_text)
    
    if med_id > 0:
        verify_medication_in_database(med_id)
    
    # Example with explicit format
    explicit_text = """HPR-nr:10017852
Prescriber: Torgny Skaret
Medication: Fosamax
Administration: Tabletten skal tas straks pasienten står opp om morgenen, sammen med et fullt glass vann på fastende mage, minst 1/2 time før inntak av annen drikke, mat eller andre legemidler. for å lette transporten til magen, og derved redusere risikoen for lokal og øsofageal irritasjon​/​bivirkning, skal pasienten sitte oppreist eller stå inntil dagens første måltid er inntatt (dvs. minst 1/2 time etter tablettinntak). tabletten skal ikke tas ved sengetid eller før en står opp. tabletten skal svelges hel. skal ikke tygges, knuses eller oppløses i munnen."""
    
    # Add explicit format to database
    print("\n\nAdding explicit format to the database...")
    explicit_med_id = add_medication_to_database(explicit_text)
    
    if explicit_med_id > 0:
        verify_medication_in_database(explicit_med_id)
    
    print("\nTest completed. See add_medication_improved.log for detailed logging information.")
