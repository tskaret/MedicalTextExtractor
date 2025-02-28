import sqlite3
import pyperclip
import os
import logging
from typing import List, Dict, Optional, Tuple

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ClipboardManager:
    """
    Manages retrieval of medication information from the database and copying to clipboard.
    """
    
    def __init__(self, db_path: str = "database/medications.db"):
        """
        Initialize the ClipboardManager with the path to the SQLite database.
        
        Args:
            db_path (str): Path to the SQLite database file
        """
        self.db_path = db_path
        self._ensure_db_exists()
        
    def _ensure_db_exists(self):
        """Ensure database directory exists"""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
            logger.info(f"Created database directory: {db_dir}")
    
    def _get_connection(self) -> sqlite3.Connection:
        """
        Get a connection to the SQLite database.
        
        Returns:
            sqlite3.Connection: Database connection object
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Return rows as dictionaries
            return conn
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {e}")
            raise
    
    def get_medications(self) -> List[Dict]:
        """
        Get a list of all medications in the database.
        
        Returns:
            List[Dict]: List of medication dictionaries with their details
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, prescriber 
                FROM medications 
                ORDER BY name
            """)
            medications = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return medications
        except sqlite3.Error as e:
            logger.error(f"Error fetching medications: {e}")
            return []
    
    def get_medication_by_name(self, name: str) -> Optional[Dict]:
        """
        Get a medication by its name.
        
        Args:
            name (str): Name of the medication to retrieve
            
        Returns:
            Optional[Dict]: Medication dictionary if found, None otherwise
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, prescriber, administration_instructions
                FROM medications
                WHERE name LIKE ?
            """, (f"%{name}%",))
            medication = cursor.fetchone()
            conn.close()
            
            if medication:
                return dict(medication)
            return None
        except sqlite3.Error as e:
            logger.error(f"Error fetching medication by name: {e}")
            return None
        
    def get_medication_by_id(self, medication_id: int) -> Optional[Dict]:
        """
        Get a medication by its ID.
        
        Args:
            medication_id (int): ID of the medication to retrieve
            
        Returns:
            Optional[Dict]: Medication dictionary if found, None otherwise
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, prescriber, administration_instructions
                FROM medications
                WHERE id = ?
            """, (medication_id,))
            medication = cursor.fetchone()
            conn.close()
            
            if medication:
                return dict(medication)
            return None
        except sqlite3.Error as e:
            logger.error(f"Error fetching medication by ID: {e}")
            return None
        
    def search_medications(self, query: str) -> List[Dict]:
        """
        Search for medications by name or prescriber.
        
        Args:
            query (str): Search string to match against medication name or prescriber
            
        Returns:
            List[Dict]: List of matching medication dictionaries
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, prescriber, administration_instructions
                FROM medications
                WHERE name LIKE ? OR prescriber LIKE ?
            """, (f"%{query}%", f"%{query}%"))
            medications = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return medications
        except sqlite3.Error as e:
            logger.error(f"Error searching medications: {e}")
            return []
        
    def copy_to_clipboard(self, text: str) -> bool:
        """
        Copy the given text to clipboard.
        
        Args:
            text (str): Text to copy to clipboard
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            pyperclip.copy(text)
            logger.info(f"Copied to clipboard: {text[:50]}...")
            return True
        except Exception as e:
            logger.error(f"Error copying to clipboard: {e}")
            return False
            
    def copy_medication_info(self, medication_id: int) -> bool:
        """
        Copy medication information to clipboard.
        
        Args:
            medication_id (int): ID of the medication to copy
            
        Returns:
            bool: True if successful, False otherwise
        """
        medication = self.get_medication_by_id(medication_id)
        if not medication:
            logger.warning(f"Medication with ID {medication_id} not found")
            return False
            
        # Format the information
        info = self._format_medication_info(medication)
        return self.copy_to_clipboard(info)
        
    def copy_instructions(self, medication_name: str) -> bool:
        """
        Copy medication administration instructions to clipboard.
        
        Args:
            medication_name (str): Name of the medication to get instructions for
            
        Returns:
            bool: True if successful, False otherwise
        """
        medication = self.get_medication_by_name(medication_name)
        if not medication:
            logger.warning(f"Medication with name '{medication_name}' not found")
            return False
            
        if not medication.get('administration_instructions'):
            logger.warning(f"No administration instructions found for '{medication_name}'")
            return False
            
        # Copy just the administration instructions to clipboard
        return self.copy_to_clipboard(medication['administration_instructions'])
    
    def _format_medication_info(self, medication: Dict) -> str:
        """
        Format medication information for clipboard.
        
        Args:
            medication (Dict): Medication dictionary
            
        Returns:
            str: Formatted medication information
        """
        return (
            f"Legemiddel: {medication['name']}\n"
            f"Rekvirent: {medication['prescriber']}\n"
            f"Administrasjonsinstruksjoner: {medication['administration_instructions']}"
        )


def main():
    """Main function to demonstrate the clipboard manager."""
    db_manager = ClipboardManager()
    
    # Example: Search for a medication and copy to clipboard
    search_term = input("Enter medication name or prescriber to search: ")
    results = db_manager.search_medications(search_term)
    
    if not results:
        print(f"No medications found for '{search_term}'")
        return
        
    print(f"Found {len(results)} medications:")
    for i, med in enumerate(results, 1):
        print(f"{i}. {med['name']} (Prescribed by: {med['prescriber']})")
        
    if len(results) == 1:
        choice = 1
    else:
        choice = int(input("Select medication number to copy to clipboard: "))
        
    if 1 <= choice <= len(results):
        selected = results[choice-1]
        db_manager.copy_medication_info(selected['id'])
        print(f"Copied information for {selected['name']} to clipboard!")
    else:
        print("Invalid selection")


if __name__ == "__main__":
    main()

