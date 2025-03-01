import os
import sqlite3
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Union

class DatabaseManager:
    """
    Manages database operations for storing and retrieving medication information.
    """
    
    def __init__(self, db_path: str):
        """
        Initialize the database manager.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        
        # Ensure the database directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Initialize the database
        self._init_db()
    
    def _init_db(self) -> None:
        """Initialize the database with required tables."""
        try:
            # Check if schema.sql exists in the same directory as the database
            schema_path = os.path.join(os.path.dirname(self.db_path), "schema.sql")
            
            if os.path.exists(schema_path):
                # Execute the schema SQL file
                with sqlite3.connect(self.db_path) as conn:
                    with open(schema_path, 'r') as f:
                        conn.executescript(f.read())
                self.logger.info(f"Database initialized from schema file: {schema_path}")
            else:
                # Create tables manually if schema file doesn't exist
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute('''
                    CREATE TABLE IF NOT EXISTS medications (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        medication_name TEXT,
                        prescriber TEXT,
                        administration TEXT,
                        original_text TEXT,
                        capture_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        confidence_score REAL DEFAULT 0.0
                    )
                    ''')
                    
                    # Create indexes for faster searching
                    conn.execute('CREATE INDEX IF NOT EXISTS idx_medication_name ON medications(medication_name)')
                    conn.execute('CREATE INDEX IF NOT EXISTS idx_prescriber ON medications(prescriber)')
                    conn.execute('CREATE INDEX IF NOT EXISTS idx_capture_date ON medications(capture_date)')
                
                self.logger.info("Database initialized with default schema")
        except Exception as e:
            self.logger.error(f"Error initializing database: {e}")
            raise
    
    def store_medication_info(self, medication_info: Dict[str, Any]) -> int:
        """
        Store medication information in the database.
        
        Args:
            medication_info: Dictionary containing medication information
        
        Returns:
            ID of the inserted record
        """
        try:
            # Extract information from the medication_info dictionary
            if isinstance(medication_info.get('medication'), dict):
                medication_name = medication_info.get('medication', {}).get('value')
                medication_confidence = medication_info.get('medication', {}).get('confidence', 0.0)
            else:
                medication_name = medication_info.get('medication')
                medication_confidence = 0.0
            
            if isinstance(medication_info.get('prescriber'), dict):
                prescriber = medication_info.get('prescriber', {}).get('value')
            else:
                prescriber = medication_info.get('prescriber')
            
            if isinstance(medication_info.get('administration'), dict):
                administration = medication_info.get('administration', {}).get('value')
            else:
                administration = medication_info.get('administration')
            
            original_text = medication_info.get('original_text', '')
            
            # Insert into database
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                INSERT INTO medications 
                (medication_name, prescriber, administration, original_text, confidence_score)
                VALUES (?, ?, ?, ?, ?)
                ''', (medication_name, prescriber, administration, original_text, medication_confidence))
                
                # Get the ID of the inserted record
                medication_id = cursor.lastrowid
                
                self.logger.info(f"Stored medication info with ID: {medication_id}")
                return medication_id
        except Exception as e:
            self.logger.error(f"Error storing medication info: {e}")
            return -1
    
    def search_medications(self, search_term: str) -> List[Dict[str, Any]]:
        """
        Search for medications in the database.
        
        Args:
            search_term: Term to search for in medication names
        
        Returns:
            List of dictionaries containing medication information
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Search in medication_name, prescriber, and administration
                cursor.execute('''
                SELECT * FROM medications
                WHERE medication_name LIKE ? OR prescriber LIKE ? OR administration LIKE ?
                ORDER BY capture_date DESC
                ''', (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
                
                # Convert rows to dictionaries
                results = []
                for row in cursor.fetchall():
                    results.append({
                        'id': row['id'],
                        'medication': row['medication_name'],
                        'prescriber': row['prescriber'],
                        'administration': row['administration'],
                        'original_text': row['original_text'],
                        'date': row['capture_date'],
                        'confidence': row['confidence_score']
                    })
                
                self.logger.info(f"Found {len(results)} results for search term: {search_term}")
                return results
        except Exception as e:
            self.logger.error(f"Error searching medications: {e}")
            return []
    
    def get_medication_by_id(self, medication_id: int) -> Optional[Dict[str, Any]]:
        """
        Get medication information by ID.
        
        Args:
            medication_id: ID of the medication record
        
        Returns:
            Dictionary containing medication information or None if not found
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('SELECT * FROM medications WHERE id = ?', (medication_id,))
                row = cursor.fetchone()
                
                if row:
                    return {
                        'id': row['id'],
                        'medication': row['medication_name'],
                        'prescriber': row['prescriber'],
                        'administration': row['administration'],
                        'original_text': row['original_text'],
                        'date': row['capture_date'],
                        'confidence': row['confidence_score']
                    }
                else:
                    self.logger.warning(f"No medication found with ID: {medication_id}")
                    return None
        except Exception as e:
            self.logger.error(f"Error getting medication by ID: {e}")
            return None
    
    def get_recent_medications(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the most recent medication records.
        
        Args:
            limit: Maximum number of records to return
        
        Returns:
            List of dictionaries containing medication information
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                SELECT * FROM medications
                ORDER BY capture_date DESC
                LIMIT ?
                ''', (limit,))
                
                # Convert rows to dictionaries
                results = []
                for row in cursor.fetchall():
                    results.append({
                        'id': row['id'],
                        'medication': row['medication_name'],
                        'prescriber': row['prescriber'],
                        'administration': row['administration'],
                        'original_text': row['original_text'],
                        'date': row['capture_date'],
                        'confidence': row['confidence_score']
                    })
                
                self.logger.info(f"Retrieved {len(results)} recent medications")
                return results
        except Exception as e:
            self.logger.error(f"Error getting recent medications: {e}")
            return []
    
    def update_medication(self, medication_id: int, updates: Dict[str, Any]) -> bool:
        """
        Update medication information.
        
        Args:
            medication_id: ID of the medication record to update
            updates: Dictionary containing fields to update
        
        Returns:
            True if update was successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Build the update query dynamically based on provided fields
                fields = []
                values = []
                
                if 'medication' in updates:
                    fields.append('medication_name = ?')
                    values.append(updates['medication'])
                
                if 'prescriber' in updates:
                    fields.append('prescriber = ?')
                    values.append(updates['prescriber'])
                
                if 'administration' in updates:
                    fields.append('administration = ?')
                    values.append(updates['administration'])
                
                if 'confidence' in updates:
                    fields.append('confidence_score = ?')
                    values.append(updates['confidence'])
                
                if not fields:
                    self.logger.warning("No fields to update")
                    return False
                
                # Add the ID to the values
                values.append(medication_id)
                
                # Execute the update query
                cursor.execute(f'''
                UPDATE medications
                SET {', '.join(fields)}
                WHERE id = ?
                ''', values)
                
                if cursor.rowcount > 0:
                    self.logger.info(f"Updated medication with ID: {medication_id}")
                    return True
                else:
                    self.logger.warning(f"No medication found with ID: {medication_id}")
                    return False
        except Exception as e:
            self.logger.error(f"Error updating medication: {e}")
            return False
    
    def delete_medication(self, medication_id: int) -> bool:
        """
        Delete a medication record.
        
        Args:
            medication_id: ID of the medication record to delete
        
        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('DELETE FROM medications WHERE id = ?', (medication_id,))
                
                if cursor.rowcount > 0:
                    self.logger.info(f"Deleted medication with ID: {medication_id}")
                    return True
                else:
                    self.logger.warning(f"No medication found with ID: {medication_id}")
                    return False
        except Exception as e:
            self.logger.error(f"Error deleting medication: {e}")
            return False
    
    def close(self) -> None:
        """Close any open database connections."""
        # SQLite connections are automatically closed when the with block exits
        # This method is included for compatibility with the interface
        self.logger.info("Database connections closed")


# Example usage
if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize database manager
    db_path = os.path.join(os.path.dirname(__file__), "medical_data.db")
    db_manager = DatabaseManager(db_path)
    
    # Example: Store medication information
    medication_info = {
        'medication': 'Paracetamol 500mg',
        'prescriber': 'Dr. Example',
        'administration': '1-2 tablets every 4-6 hours as needed',
        'original_text': 'Sample prescription text'
    }
    
    med_id = db_manager.store_medication_info(medication_info)
    print(f"Stored medication with ID: {med_id}")
    
    # Example: Search for medications
    results = db_manager.search_medications('Paracetamol')
    print(f"Found {len(results)} results for 'Paracetamol'")
    for result in results:
        print(f"- {result['medication']} (Prescribed by: {result['prescriber']})")
    
    # Close the database
    db_manager.close()
