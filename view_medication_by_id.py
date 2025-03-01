#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to view a specific medication by ID.
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
        logging.FileHandler("view_medication.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def view_medication_by_id(medication_id):
    """View a specific medication by ID."""
    # Set database path
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                          "database", "medical_data.db")
    
    # Initialize database manager
    db_manager = DatabaseManager(db_path)
    
    # Get medication by ID
    medication = db_manager.get_medication_by_id(medication_id)
    
    if medication:
        print("\nMedication Details:")
        print("=" * 80)
        print(f"ID: {medication['id']}")
        print(f"Medication: {medication['medication']}")
        print(f"Prescriber: {medication['prescriber']}")
        print(f"Administration: {medication['administration']}")
        print(f"Date: {medication['date']}")
        print("=" * 80)
        
        logger.info(f"Viewed medication with ID {medication_id}")
    else:
        print(f"No medication found with ID {medication_id}")
        logger.warning(f"No medication found with ID {medication_id}")
    
    # Close database connection
    db_manager.close()

if __name__ == "__main__":
    print("=" * 80)
    print("VIEWING MEDICATION BY ID")
    print("=" * 80)
    
    # Get medication ID from command line argument or prompt user
    if len(sys.argv) > 1:
        try:
            medication_id = int(sys.argv[1])
        except ValueError:
            print("Invalid medication ID. Please provide a valid integer ID.")
            sys.exit(1)
    else:
        try:
            medication_id = int(input("Enter medication ID: "))
        except ValueError:
            print("Invalid medication ID. Please provide a valid integer ID.")
            sys.exit(1)
    
    view_medication_by_id(medication_id)
    
    print("\nOperation completed. See view_medication.log for detailed logging information.")
