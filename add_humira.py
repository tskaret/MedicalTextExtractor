#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to add Humira medication to the database using the improved text analyzer.
"""

import os
import logging
from database.db_manager import DatabaseManager
from improved_text_analyzer import ImprovedTextAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("add_humira.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def add_humira_to_database():
    """Add Humira medication information to the database."""
    # Set database path
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                          "database", "medical_data.db")
    
    # Initialize database manager
    db_manager = DatabaseManager(db_path)
    
    # Initialize improved text analyzer
    analyzer = ImprovedTextAnalyzer()
    
    # Humira medication text
    humira_text = """HPR-nr:10011122
Prescriber: Kari Olavsdottir
Medication: Humira
Administration: Første dose på 80 mg (to 40 mg injeksjoner på én dag), etterfulgt av 40 mg annenhver uke som starter én uke etter den første dosen."""
    
    # Analyze the text
    print("Analyzing Humira medication text...")
    extracted_info = analyzer.analyze_text(humira_text)
    
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
        'original_text': humira_text
    }
    
    # Store in database
    med_id = db_manager.store_medication_info(medication_info)
    
    if med_id > 0:
        print(f"\nSuccessfully added {medication_info['medication']} to the database with ID: {med_id}")
        logger.info(f"Added {medication_info['medication']} to database with ID: {med_id}")
        
        # Verify that the medication was added
        medication = db_manager.get_medication_by_id(med_id)
        
        if medication:
            print("\nVerification - Medication found in database:")
            print(f"ID: {medication['id']}")
            print(f"Medication: {medication['medication']}")
            print(f"Prescriber: {medication['prescriber']}")
            print(f"Administration: {medication['administration']}")
            print(f"Date: {medication['date']}")
        else:
            print(f"Medication with ID {med_id} not found in database")
    else:
        print("\nFailed to add medication to the database")
        logger.error("Failed to add medication to database")
    
    # Close database connection
    db_manager.close()
    
    return med_id

if __name__ == "__main__":
    print("=" * 80)
    print("ADDING HUMIRA TO DATABASE USING IMPROVED TEXT ANALYZER")
    print("=" * 80)
    
    add_humira_to_database()
    
    print("\nOperation completed. See add_humira.log for detailed logging information.")
