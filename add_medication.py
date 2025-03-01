#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to add a medication to the database manually.
This can be used for testing or to pre-populate the database with known medications.
"""

import os
import sys
import logging
from database.db_manager import DatabaseManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("add_medication.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def add_fosamax_to_database():
    """Add Fosamax medication information to the database."""
    # Set database path
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                          "database", "medical_data.db")
    
    # Initialize database manager
    db_manager = DatabaseManager(db_path)
    
    # Medication information
    medication_info = {
        'medication': 'Fosamax',
        'prescriber': 'Dr. Torgny Skaret (10017852)',
        'administration': """Tabletten skal tas straks pasienten står opp om morgenen, sammen med et fullt glass vann på fastende mage, minst 1/2 time før inntak av annen drikke, mat eller andre legemidler. For å lette transporten til magen, og derved redusere risikoen for lokal og øsofageal irritasjon​/​bivirkning, skal pasienten sitte oppreist eller stå inntil dagens første måltid er inntatt (dvs. minst 1/2 time etter tablettinntak). Tabletten skal ikke tas ved sengetid eller før en står opp. Tabletten skal svelges hel. Skal ikke tygges, knuses eller oppløses i munnen.""",
        'original_text': """Fosamax

Tabletten skal tas straks pasienten står opp om morgenen, sammen med et fullt glass vann på fastende mage, minst 1/2 time før inntak av annen drikke, mat eller andre legemidler. For å lette transporten til magen, og derved redusere risikoen for lokal og øsofageal irritasjon​/​bivirkning, skal pasienten sitte oppreist eller stå inntil dagens første måltid er inntatt (dvs. minst 1/2 time etter tablettinntak). Tabletten skal ikke tas ved sengetid eller før en står opp. Tabletten skal svelges hel. Skal ikke tygges, knuses eller oppløses i munnen.

doctor 10017852, Torgny Skaret"""
    }
    
    # Store in database
    med_id = db_manager.store_medication_info(medication_info)
    
    if med_id > 0:
        print(f"Successfully added Fosamax to the database with ID: {med_id}")
        logger.info(f"Added Fosamax to database with ID: {med_id}")
    else:
        print("Failed to add Fosamax to the database")
        logger.error("Failed to add Fosamax to database")
    
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
    print("Adding Fosamax to the database...")
    med_id = add_fosamax_to_database()
    
    if med_id > 0:
        verify_medication_in_database(med_id)
