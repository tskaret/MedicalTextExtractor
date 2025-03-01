#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to view medications in the database.
"""

import os
import sqlite3
from database.db_manager import DatabaseManager

def view_medications():
    """View all medications in the database."""
    # Set database path
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                          "database", "medical_data.db")
    
    # Initialize database manager
    db_manager = DatabaseManager(db_path)
    
    # Get all medications (using get_recent_medications with a high limit)
    medications = db_manager.get_recent_medications(limit=100)
    
    if medications:
        print(f"Found {len(medications)} medications in the database:\n")
        print("ID | Medication | Prescriber | Administration | Date")
        print("-" * 80)
        
        for med in medications:
            # Truncate administration text for display
            admin_text = med['administration'][:50] + "..." if med['administration'] and len(med['administration']) > 50 else med['administration']
            
            print(f"{med['id']} | {med['medication']} | {med['prescriber']} | {admin_text} | {med['date']}")
    else:
        print("No medications found in the database.")
    
    # Close database connection
    db_manager.close()

if __name__ == "__main__":
    print("=" * 80)
    print("VIEWING MEDICATIONS IN DATABASE")
    print("=" * 80)
    
    view_medications()
