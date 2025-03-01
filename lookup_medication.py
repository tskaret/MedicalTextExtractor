#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to look up medication information in the database.
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
        logging.FileHandler("lookup_medication.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def lookup_medication(medication_name, silent=False):
    """Look up medication information in the database."""
    # Set database path
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                          "database", "medical_data.db")
    
    # Initialize database manager
    db_manager = DatabaseManager(db_path)
    
    # Search for the medication
    results = db_manager.search_medications(medication_name)
    
    if not silent:
        if results:
            print(f"\nFound {len(results)} results for '{medication_name}':")
            
            # Display each result
            for i, med in enumerate(results, 1):
                print(f"\nResult {i}:")
                print("=" * 80)
                print(f"ID: {med['id']}")
                print(f"Medication: {med['medication']}")
                print(f"Prescriber: {med['prescriber']}")
                print(f"\nAdministration Instructions:")
                print("-" * 80)
                print(f"{med['administration']}")
                print("=" * 80)
        else:
            print(f"No results found for '{medication_name}'")
    
    # Close database connection
    db_manager.close()
    
    return results

if __name__ == "__main__":
    print("=" * 80)
    print("MEDICATION LOOKUP")
    print("=" * 80)
    
    # Get medication name from command line argument or prompt user
    if len(sys.argv) > 1:
        medication_name = sys.argv[1]
    else:
        medication_name = input("Enter medication name to look up: ")
    
    lookup_medication(medication_name)
    
    print("\nOperation completed. See lookup_medication.log for detailed logging information.")
