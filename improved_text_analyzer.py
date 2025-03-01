#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Improved Text Analyzer with better support for various medication information formats.
"""

import re
import logging
from typing import Dict, List, Optional, Tuple, Any
from text_analyzer import TextAnalyzer as BaseTextAnalyzer

class ImprovedTextAnalyzer(BaseTextAnalyzer):
    """
    An improved version of the TextAnalyzer class with better support for
    various medication information formats.
    """
    
    def __init__(self):
        """Initialize the improved text analyzer."""
        super().__init__()
        self.logger = logging.getLogger(__name__)
        
        # Add additional keywords and patterns
        self.keywords['prescriber'].extend(['doctor', 'lege', 'dr'])
        
        # Additional patterns for different formats
        self.patterns.update({
            'doctor_id': r'(?:doctor|lege|dr|HPR-nr)[.\s:]+(\d+)[,\s]*([^\n]+)?',
            'medication_first_line': r'^([A-Za-z0-9\s\-]+)(?:\n|\r\n?)',
            'administration_block': r'(?:^|\n)([A-Za-z].*?(?:tas|brukes|svelges|administreres).*?)(?:\n\n|\Z)',
            'explicit_hpr': r'HPR-nr:(\d+)',
            'explicit_prescriber': r'Prescriber:\s*([^\n]+)',
            'explicit_medication': r'Medication:\s*([^\n]+)',
            'explicit_administration': r'Administration:\s*([^\n]+(?:\n[^\n]+)*)',
            'hpr_format': r'HPR:?\s*(\d+)',
            'legemiddel_format': r'Legemiddel:?\s*([^\n]+)'
        })
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Analyze OCR text with improved format handling.
        
        Args:
            text: The OCR text to analyze
        
        Returns:
            Dictionary containing extracted information
        """
        if not text or not isinstance(text, str):
            self.logger.warning("Invalid text input for analysis")
            return {}
        
        # Check if this is an explicit format first
        result = self._extract_explicit_format(text)
        if result and all(key in result for key in ['hpr_number', 'prescriber', 'medication', 'administration']):
            # If we found all fields in explicit format, return it
            result['original_text'] = text
            return result
        
        # If not explicit format or missing fields, try standard extraction
        # Normalize text for better matching
        normalized_text = self._normalize_text(text)
        
        # Try standard extraction
        result = super().analyze_text(text)
        
        # Extract doctor information
        doctor_info = self._extract_doctor_with_id(normalized_text)
        if doctor_info:
            result['hpr_number'] = doctor_info['hpr_number']
            result['prescriber'] = doctor_info['name']
        elif not result.get('prescriber') or result.get('prescriber') == 'midler':
            # Try to find any prescriber information
            prescriber = self._extract_any_prescriber(normalized_text)
            if prescriber:
                result['prescriber'] = prescriber
        
        # Extract medication name
        if not result.get('medication'):
            medication = self._extract_medication_from_first_line(text)
            if medication:
                result['medication'] = medication
        
        # Extract administration instructions
        if not result.get('administration'):
            administration = self._extract_administration_block(normalized_text)
            if administration:
                result['administration'] = administration
        
        # Clean up the administration text to remove doctor information
        if result.get('administration'):
            result['administration'] = self._clean_administration_text(result['administration'], result.get('medication'))
        
        # Format the administration text with proper capitalization
        if result.get('administration'):
            result['administration'] = self._format_administration_text(result['administration'])
        
        # Store original text
        result['original_text'] = text
        
        return result
    
    def _extract_explicit_format(self, text: str) -> Dict[str, Any]:
        """
        Extract information from explicitly formatted text.
        
        Args:
            text: Text in explicit format
            
        Returns:
            Dictionary with extracted information
        """
        result = {}
        
        # Extract HPR number
        hpr_match = re.search(self.patterns['explicit_hpr'], text, re.IGNORECASE | re.MULTILINE)
        if hpr_match:
            result['hpr_number'] = hpr_match.group(1).strip()
        else:
            # Try alternative HPR format
            hpr_alt_match = re.search(self.patterns['hpr_format'], text, re.IGNORECASE | re.MULTILINE)
            if hpr_alt_match:
                result['hpr_number'] = hpr_alt_match.group(1).strip()
        
        # Extract prescriber
        prescriber_match = re.search(self.patterns['explicit_prescriber'], text, re.IGNORECASE | re.MULTILINE)
        if prescriber_match:
            result['prescriber'] = prescriber_match.group(1).strip()
        
        # Extract medication
        medication_match = re.search(self.patterns['explicit_medication'], text, re.IGNORECASE | re.MULTILINE)
        if medication_match:
            result['medication'] = medication_match.group(1).strip()
        else:
            # Try alternative medication format
            med_alt_match = re.search(self.patterns['legemiddel_format'], text, re.IGNORECASE | re.MULTILINE)
            if med_alt_match:
                result['medication'] = med_alt_match.group(1).strip()
        
        # Extract administration
        admin_match = re.search(self.patterns['explicit_administration'], text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
        if admin_match:
            result['administration'] = admin_match.group(1).strip()
        
        return result
    
    def _extract_doctor_with_id(self, text: str) -> Optional[Dict[str, str]]:
        """
        Extract doctor information with ID number.
        
        Args:
            text: Normalized text to extract from
        
        Returns:
            Dictionary with doctor name and HPR number or None if not found
        """
        # Try to match HPR-nr pattern
        match = re.search(r'HPR-nr[.\s:]*(\d+)', text, re.IGNORECASE | re.MULTILINE)
        if match:
            hpr_number = match.group(1).strip()
            
            # Try to find the name separately
            name_match = re.search(r'Prescriber[.\s:]*([^\n]+)', text, re.IGNORECASE | re.MULTILINE)
            if name_match:
                return {
                    'hpr_number': hpr_number,
                    'name': name_match.group(1).strip()
                }
        
        # Try standard doctor pattern
        match = re.search(self.patterns['doctor_id'], text, re.IGNORECASE | re.MULTILINE)
        if match:
            hpr_number = match.group(1).strip()
            name = match.group(2).strip() if match.group(2) else "Unknown"
            return {
                'hpr_number': hpr_number,
                'name': name
            }
        
        # Try a more flexible pattern if the first one fails
        match = re.search(r'doctor\s+(\d+)[,\s]+([^\n]+)', text, re.IGNORECASE | re.MULTILINE)
        if match:
            hpr_number = match.group(1).strip()
            name = match.group(2).strip()
            return {
                'hpr_number': hpr_number,
                'name': name
            }
        
        return None
    
    def _extract_any_prescriber(self, text: str) -> Optional[str]:
        """
        Extract any prescriber information from the text.
        
        Args:
            text: Text to extract from
        
        Returns:
            Extracted prescriber name or None if not found
        """
        # Try to match prescriber pattern
        match = re.search(r'Prescriber[.\s:]*([^\n]+)', text, re.IGNORECASE | re.MULTILINE)
        if match:
            return match.group(1).strip()
        
        return None
    
    def _extract_medication_from_first_line(self, text: str) -> Optional[str]:
        """
        Extract medication name from the first line of text.
        
        Args:
            text: Text to extract from
        
        Returns:
            Extracted medication name or None if not found
        """
        # Try to match medication pattern
        match = re.search(r'Medication[.\s:]*([^\n]+)', text, re.IGNORECASE | re.MULTILINE)
        if match:
            return match.group(1).strip()
        
        # Clean the text by removing leading/trailing whitespace
        cleaned_text = text.strip()
        
        # Try to match the first line as medication name
        match = re.search(self.patterns['medication_first_line'], cleaned_text, re.MULTILINE)
        if match:
            medication = match.group(1).strip()
            # Verify it's not too long (likely not a medication name if too long)
            if len(medication) < 30:
                return medication
        
        # If no match or too long, try the first line directly
        lines = cleaned_text.split('\n')
        if lines and lines[0].strip() and len(lines[0].strip()) < 30:
            return lines[0].strip()
        
        return None
    
    def _extract_administration_block(self, text: str) -> Optional[str]:
        """
        Extract a block of text that likely contains administration instructions.
        
        Args:
            text: Text to extract from
        
        Returns:
            Extracted administration block or None if not found
        """
        # Try to match administration pattern
        match = re.search(r'Administration[.\s:]*([^\n]+(?:\n[^\n]+)*)', text, re.IGNORECASE | re.MULTILINE)
        if match:
            return match.group(1).strip()
        
        # First try to find a paragraph that contains administration instructions
        match = re.search(self.patterns['administration_block'], text, re.IGNORECASE | re.DOTALL | re.MULTILINE)
        if match:
            return match.group(1).strip()
        
        # If that fails, try to extract the largest paragraph
        paragraphs = re.split(r'\n\s*\n', text)
        if paragraphs:
            # Find the longest paragraph that's not just a few words
            longest = max(paragraphs, key=len)
            if len(longest) > 100:  # Only return if it's substantial
                return longest.strip()
        
        return None
    
    def _clean_administration_text(self, text: str, medication: Optional[str] = None) -> str:
        """
        Clean up administration text by removing doctor information.
        
        Args:
            text: Administration text to clean
            medication: Medication name to check for duplication
        
        Returns:
            Cleaned administration text
        """
        # Remove doctor information from administration text
        cleaned = re.sub(r'doctor\s+\d+[,\s]+[^\n]+', '', text, flags=re.IGNORECASE)
        
        # Remove any medication name from the beginning if it's duplicated
        if medication and cleaned.lower().startswith(medication.lower()):
            cleaned = cleaned[len(medication):].strip()
        
        return cleaned.strip()
    
    def _format_administration_text(self, text: str) -> str:
        """
        Format administration text with proper capitalization.
        
        Args:
            text: Administration text to format
        
        Returns:
            Formatted administration text
        """
        # Capitalize the first letter of the text
        if text:
            return text[0].upper() + text[1:]
        return text


# Example usage
if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Example OCR text
    sample_text = """Fosamax

Tabletten skal tas straks pasienten står opp om morgenen, sammen med et fullt glass vann på fastende mage, minst 1/2 time før inntak av annen drikke, mat eller andre legemidler. For å lette transporten til magen, og derved redusere risikoen for lokal og øsofageal irritasjon​/​bivirkning, skal pasienten sitte oppreist eller stå inntil dagens første måltid er inntatt (dvs. minst 1/2 time etter tablettinntak). Tabletten skal ikke tas ved sengetid eller før en står opp. Tabletten skal svelges hel. Skal ikke tygges, knuses eller oppløses i munnen.

doctor 10017852, Torgny Skaret"""
    
    # Initialize the improved analyzer
    analyzer = ImprovedTextAnalyzer()
    
    # Analyze the text
    result = analyzer.analyze_text(sample_text)
    
    # Print results
    print("Extracted Information:")
    print(f"HPR-nr: {result.get('hpr_number', 'Not found')}")
    print(f"Prescriber: {result.get('prescriber', 'Not found')}")
    print(f"Medication: {result.get('medication', 'Not found')}")
    print(f"Administration: {result.get('administration', 'Not found')}")
    
    # Example with explicit format
    explicit_text = """HPR-nr:10017852
Prescriber: Torgny Skaret
Medication: Fosamax
Administration: Tabletten skal tas straks pasienten står opp om morgenen, sammen med et fullt glass vann på fastende mage, minst 1/2 time før inntak av annen drikke, mat eller andre legemidler. for å lette transporten til magen, og derved redusere risikoen for lokal og øsofageal irritasjon​/​bivirkning, skal pasienten sitte oppreist eller stå inntil dagens første måltid er inntatt (dvs. minst 1/2 time etter tablettinntak). tabletten skal ikke tas ved sengetid eller før en står opp. tabletten skal svelges hel. skal ikke tygges, knuses eller oppløses i munnen."""
    
    # Analyze the explicit format
    explicit_result = analyzer.analyze_text(explicit_text)
    
    print("\nExplicit Format - Extracted Information:")
    print(f"HPR-nr: {explicit_result.get('hpr_number', 'Not found')}")
    print(f"Prescriber: {explicit_result.get('prescriber', 'Not found')}")
    print(f"Medication: {explicit_result.get('medication', 'Not found')}")
    print(f"Administration: {explicit_result.get('administration', 'Not found')}")
