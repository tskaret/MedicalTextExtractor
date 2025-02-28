import re
import logging
from typing import Dict, List, Optional, Tuple, Any

class TextAnalyzer:
    """
    A class for analyzing and extracting medication information from OCR text.
    Specifically targets Norwegian medical terms like "rekvirent" (prescriber) and
    "Legemiddel" (drug), along with administration instructions.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Define keywords and patterns to look for
        self.keywords = {
            'prescriber': ['rekvirent', 'lege', 'forskriver'],
            'medication': ['legemiddel', 'medisin', 'preparat'],
            'administration': ['dosering', 'bruksanvisning', 'administrering', 'bruk', 'tas', 'brukes']
        }
        
        # Regular expressions for extracting information
        self.patterns = {
            'prescriber': r'(?:rekvirent|lege|forskriver)[:\s]+([^\n]+)',
            'medication': r'(?:legemiddel|medisin|preparat)[:\s]+([^\n]+)',
            'admin_simple': r'(?:dosering|bruksanvisning|administrering)[:\s]+([^\n]+)'
        }
        
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Analyze OCR text and extract relevant medication information.
        
        Args:
            text: The OCR text to analyze
        
        Returns:
            Dictionary containing extracted information
        """
        if not text or not isinstance(text, str):
            self.logger.warning("Invalid text input for analysis")
            return {}
        
        # Normalize text for better matching
        normalized_text = self._normalize_text(text)
        
        # Extract information
        result = {
            'prescriber': self.extract_prescriber(normalized_text),
            'medication': self.extract_medication(normalized_text),
            'administration': self.extract_administration_instructions(normalized_text),
            'original_text': text
        }
        
        return result
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Alias for analyze_text() to maintain compatibility with main.py.
        
        Args:
            text: The OCR text to analyze
        
        Returns:
            Dictionary containing extracted information
        """
        return self.analyze_text(text)
    
    def _normalize_text(self, text: str) -> str:
        """
        Normalize text by converting to lowercase, fixing common OCR errors,
        and standardizing whitespace.
        
        Args:
            text: Text to normalize
        
        Returns:
            Normalized text
        """
        # Convert to lowercase
        text = text.lower()
        
        # Fix common OCR errors specific to Norwegian medical terms
        ocr_fixes = {
            'rekvirenl': 'rekvirent',
            'legemiddei': 'legemiddel',
            'legerniddel': 'legemiddel',
            # Add more OCR error corrections as needed
        }
        
        for error, correction in ocr_fixes.items():
            text = text.replace(error, correction)
        
        # Standardize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text
    
    def extract_prescriber(self, text: str) -> Optional[str]:
        """
        Extract prescriber information from the text.
        
        Args:
            text: Normalized text to extract from
        
        Returns:
            Extracted prescriber information or None if not found
        """
        match = re.search(self.patterns['prescriber'], text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        
        # Fall back to context-based extraction if regex fails
        return self._extract_context(text, self.keywords['prescriber'], 50)
    
    def extract_medication(self, text: str) -> Optional[str]:
        """
        Extract medication information from the text.
        
        Args:
            text: Normalized text to extract from
        
        Returns:
            Extracted medication information or None if not found
        """
        match = re.search(self.patterns['medication'], text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        
        # Fall back to context-based extraction if regex fails
        return self._extract_context(text, self.keywords['medication'], 50)
    
    def extract_administration_instructions(self, text: str) -> Optional[str]:
        """
        Extract administration instructions from the text.
        This is more complex as instructions can span multiple lines
        and may not follow a simple pattern.
        
        Args:
            text: Normalized text to extract from
        
        Returns:
            Extracted administration instructions or None if not found
        """
        # Try simple pattern first
        match = re.search(self.patterns['admin_simple'], text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        
        # Look for sections that might contain administration instructions
        admin_section = self._find_administration_section(text)
        if admin_section:
            return admin_section
        
        # Fall back to context-based extraction
        return self._extract_context(text, self.keywords['administration'], 100)
    
    def _extract_context(self, text: str, keywords: List[str], context_size: int) -> Optional[str]:
        """
        Extract context around keywords.
        
        Args:
            text: Text to search in
            keywords: List of keywords to search for
            context_size: Number of characters to extract after the keyword
        
        Returns:
            Extracted context or None if no keywords found
        """
        for keyword in keywords:
            idx = text.find(keyword)
            if idx != -1:
                # Find the end of the current sentence or line
                start_idx = idx + len(keyword)
                end_idx = start_idx + context_size
                
                # Try to find natural boundaries
                period_idx = text.find('.', start_idx, end_idx)
                newline_idx = text.find('\n', start_idx, end_idx)
                
                if period_idx != -1:
                    end_idx = period_idx
                elif newline_idx != -1:
                    end_idx = newline_idx
                
                # Extract and clean the context
                context = text[start_idx:end_idx].strip()
                context = re.sub(r'^[:\s]+', '', context)  # Remove leading colons and whitespace
                
                if context:
                    return context
        
        return None
    
    def _find_administration_section(self, text: str) -> Optional[str]:
        """
        Find a section in the text that likely contains administration instructions.
        
        Args:
            text: Text to search in
        
        Returns:
            Section containing administration instructions or None if not found
        """
        # Split text into sections/paragraphs
        sections = re.split(r'\n\s*\n', text)
        
        for section in sections:
            section = section.strip()
            if not section:
                continue
            
            # Check if the section contains administration keywords
            if any(keyword in section for keyword in self.keywords['administration']):
                # Remove any section headers
                cleaned_section = re.sub(r'^.*?:', '', section).strip()
                if cleaned_section:
                    return cleaned_section
                return section
        
        return None
    
    def get_structured_data(self, text: str) -> Dict[str, Any]:
        """
        Process text and return structured data with confidence scores.
        
        Args:
            text: OCR text to analyze
        
        Returns:
            Dictionary with structured data and confidence scores
        """
        analysis = self.analyze_text(text)
        
        # Add confidence scores (simple implementation)
        result = {
            'prescriber': {
                'value': analysis.get('prescriber', None),
                'confidence': self._calculate_confidence(analysis.get('prescriber', ''))
            },
            'medication': {
                'value': analysis.get('medication', None),
                'confidence': self._calculate_confidence(analysis.get('medication', ''))
            },
            'administration': {
                'value': analysis.get('administration', None),
                'confidence': self._calculate_confidence(analysis.get('administration', ''))
            },
            'original_text': analysis.get('original_text', '')
        }
        
        return result
    
    def _calculate_confidence(self, text: Optional[str]) -> float:
        """
        Calculate a simple confidence score for extracted text.
        
        Args:
            text: Extracted text
        
        Returns:
            Confidence score between 0.0 and 1.0
        """
        if not text:
            return 0.0
        
        # Very simple confidence calculation based on text length
        # In a real application, this would be more sophisticated
        if len(text) < 3:
            return 0.1
        elif len(text) < 10:
            return 0.5
        else:
            return 0.8


# Example usage
if __name__ == "__main__":
    # Example OCR text
    sample_text = """
    Resept
    
    Rekvirent: Dr. Jansen, Oslo Legesenter
    Legemiddel: Paracetamol 500mg tabletter
    
    Dosering: 1-2 tabletter inntil 4 ganger daglig ved behov.
    Maksimal dose: 8 tabletter per døgn.
    
    Utlevert: 100 tabletter
    Dato: 15.06.2023
    """
    
    analyzer = TextAnalyzer()
    result = analyzer.get_structured_data(sample_text)
    
    print("Extracted Information:")
    print(f"Prescriber: {result['prescriber']['value']} (Confidence: {result['prescriber']['confidence']:.2f})")
    print(f"Medication: {result['medication']['value']} (Confidence: {result['medication']['confidence']:.2f})")
    print(f"Administration: {result['administration']['value']} (Confidence: {result['administration']['confidence']:.2f})")

