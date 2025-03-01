#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Comprehensive test script for evaluating the TextAnalyzer with a wide variety of
medication information formats, including edge cases and custom formats.

This script:
1. Tests existing format files
2. Tests custom formats defined in the script
3. Evaluates the analyzer's performance with each format
4. Provides suggestions for improving the analyzer
"""

import os
import sys
import logging
import json
from pathlib import Path
from text_analyzer import TextAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("comprehensive_test_results.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Define custom test cases
CUSTOM_TEST_CASES = [
    {
        "name": "Minimal Format",
        "text": """
        Medisin: Ibuprofen 400mg
        Dosering: 1 tablett 3 ganger daglig
        """
    },
    {
        "name": "Hospital Format",
        "text": """
        UNIVERSITETSSYKEHUSET NORD-NORGE
        Avdeling: Medisinsk
        
        ORDINASJONSKORT
        
        Pasient: Hansen, Nils (12.05.1965)
        Journal: 123456
        
        Ordinert av: Overlege Dr. Kristin Svendsen
        
        MEDIKAMENT: Warfarin Orion 2,5 mg
        
        ADMINISTRASJON:
        Mandag: 1 tablett
        Tirsdag: 1/2 tablett
        Onsdag: 1 tablett
        Torsdag: 1/2 tablett
        Fredag: 1 tablett
        Lørdag: 1/2 tablett
        Søndag: 1/2 tablett
        
        INR-kontroll hver 4. uke
        Målverdi INR: 2,0-3,0
        """
    },
    {
        "name": "Pharmacy Label Format",
        "text": """
        APOTEK 1 STORTORGET
        Tlf: 815 22 333
        
        PARACET 500 mg tabletter
        100 stk
        
        Til: Jensen, Lise
        
        DOSERING:
        1-2 tabletter inntil 3-4 ganger daglig ved behov.
        Maksimalt 8 tabletter per døgn.
        
        Utlevert: 01.03.2023
        Exp: 01.03.2025
        """
    },
    {
        "name": "E-prescription Format",
        "text": """
        E-RESEPT
        ID: 8765432
        
        Forskriver: Dr. Anders Larsen (HPR: 12345)
        Institusjon: Legegruppen Sentrum
        
        Pasient: Pedersen, Knut (280590-12345)
        
        Legemiddel: Metoprolol Sandoz 50 mg depottabletter
        Varenr: 113344
        Antall: 100 stk
        
        Dosering: 1 tablett morgen og kveld
        
        Bruksområde: Mot høyt blodtrykk og hjertebank
        Refusjon: §2 Hjerte-karsykdommer
        
        Gyldig til: 01.09.2023
        """
    },
    {
        "name": "Mixed Language Format",
        "text": """
        PRESCRIPTION / RESEPT
        
        Doctor / Lege: Dr. James Wilson
        Hospital / Sykehus: Oslo International Medical Center
        
        Patient / Pasient: Smith, John
        DOB / Fødselsdato: 10.11.1980
        
        Medication / Legemiddel: Amoxicillin 500mg capsules
        
        Dosage / Dosering: 
        Take one capsule three times daily with food
        Ta en kapsel tre ganger daglig med mat
        
        Duration / Varighet: 7 days / 7 dager
        
        Date / Dato: 15.02.2023
        """
    },
    {
        "name": "Extreme OCR Errors",
        "text": """
        R3S3PT
        
        R€kv1rent: 0r. 0|af J0hann$en
        L€g€$€nt€r: 0$|0 H€|$€$€nt€r
        
        Pa$!ent: Han$€n, P€r
        
        L€g€rnidd€|: S€rtra|in 50rng tab|€tt€r
        
        D0$€ring: 1 tab|€tt dag|ig, h€|$t 0rn rn0rg€n€n
        
        Ut$kr€v€t: 10.04.2O23
        """
    },
    {
        "name": "No Keywords Format",
        "text": """
        Dr. Anita Sørensen
        Bergåsen Legesenter
        
        Til pasient Trond Olsen
        
        Simvastatin 20mg
        
        En tablett daglig om kvelden
        
        Mot høyt kolesterol
        Unngå grapefruktjuice
        
        15.01.2023
        """
    },
    {
        "name": "Handwritten OCR Simulation",
        "text": """
        Resept
        
        Dr. Kari Nordmann
        Legekontoret i Fjorden
        
        Pasient: Ole Hansen
        
        Amlodipin 5 mg
        
        1 tablett daglig
        
        Mot høyt blodtrykk
        
        01/02/2023
        """
    }
]

def load_test_data(file_path):
    """Load test data from a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        logger.error(f"Error loading test data from {file_path}: {e}")
        return None

def print_analysis_results(format_name, text, results, expected=None):
    """Print the analysis results in a formatted way."""
    print(f"\n{'=' * 80}")
    print(f"FORMAT: {format_name}")
    print(f"{'=' * 80}")
    
    # Print original text (truncated if too long)
    max_text_length = 300
    if len(text) > max_text_length:
        display_text = text[:max_text_length] + "..."
    else:
        display_text = text
    print(f"ORIGINAL TEXT:\n{display_text}\n")
    
    # Print extracted information
    print("EXTRACTED INFORMATION:")
    prescriber = results.get('prescriber', {}).get('value') if isinstance(results.get('prescriber'), dict) else results.get('prescriber')
    medication = results.get('medication', {}).get('value') if isinstance(results.get('medication'), dict) else results.get('medication')
    administration = results.get('administration', {}).get('value') if isinstance(results.get('administration'), dict) else results.get('administration')
    
    print(f"Prescriber: {prescriber or 'Not found'}")
    print(f"Medication: {medication or 'Not found'}")
    print(f"Administration: {administration or 'Not found'}")
    
    # Print confidence scores if available
    if 'prescriber' in results and isinstance(results['prescriber'], dict) and 'confidence' in results['prescriber']:
        print("\nCONFIDENCE SCORES:")
        print(f"Prescriber: {results['prescriber'].get('confidence', 0):.2f}")
        print(f"Medication: {results['medication'].get('confidence', 0):.2f}")
        print(f"Administration: {results['administration'].get('confidence', 0):.2f}")
    
    # Compare with expected results if provided
    if expected:
        print("\nEVALUATION:")
        prescriber_match = "✓" if prescriber and expected.get('prescriber') and prescriber.lower() in expected.get('prescriber').lower() else "✗"
        medication_match = "✓" if medication and expected.get('medication') and medication.lower() in expected.get('medication').lower() else "✗"
        admin_match = "✓" if administration and expected.get('administration') and administration.lower() in expected.get('administration').lower() else "✗"
        
        print(f"Prescriber: {prescriber_match} {'(Expected: ' + expected.get('prescriber') + ')' if prescriber_match == '✗' else ''}")
        print(f"Medication: {medication_match} {'(Expected: ' + expected.get('medication') + ')' if medication_match == '✗' else ''}")
        print(f"Administration: {admin_match} {'(Expected: ' + expected.get('administration') + ')' if admin_match == '✗' else ''}")

def evaluate_analyzer_performance(results, test_cases_count):
    """Evaluate the overall performance of the analyzer."""
    prescriber_found = sum(1 for r in results if r.get('prescriber_found'))
    medication_found = sum(1 for r in results if r.get('medication_found'))
    administration_found = sum(1 for r in results if r.get('administration_found'))
    
    print(f"\n{'=' * 80}")
    print("OVERALL PERFORMANCE EVALUATION")
    print(f"{'=' * 80}")
    print(f"Total test cases: {test_cases_count}")
    print(f"Prescriber identified: {prescriber_found}/{test_cases_count} ({prescriber_found/test_cases_count*100:.1f}%)")
    print(f"Medication identified: {medication_found}/{test_cases_count} ({medication_found/test_cases_count*100:.1f}%)")
    print(f"Administration identified: {administration_found}/{test_cases_count} ({administration_found/test_cases_count*100:.1f}%)")
    
    # Calculate overall score
    overall_score = (prescriber_found + medication_found + administration_found) / (test_cases_count * 3) * 100
    print(f"Overall extraction rate: {overall_score:.1f}%")
    
    # Provide performance assessment
    if overall_score >= 90:
        print("\nPerformance Assessment: EXCELLENT")
        print("The analyzer performs very well across different formats.")
    elif overall_score >= 75:
        print("\nPerformance Assessment: GOOD")
        print("The analyzer performs well but could be improved for certain formats.")
    elif overall_score >= 50:
        print("\nPerformance Assessment: FAIR")
        print("The analyzer needs significant improvements to handle various formats reliably.")
    else:
        print("\nPerformance Assessment: POOR")
        print("The analyzer struggles with most formats and needs a major overhaul.")

def main():
    """Main function to run the comprehensive format tests."""
    # Initialize the text analyzer
    analyzer = TextAnalyzer()
    
    # Define test data files
    test_dir = Path("test_data")
    file_test_cases = {
        "Standard Format": {
            "file": test_dir / "standard_format.txt",
            "expected": {
                "prescriber": "Dr. Erik Hansen",
                "medication": "Paracetamol 500mg tabletter",
                "administration": "1-2 tabletter hver 4-6 time ved behov"
            }
        },
        "Alternative Format": {
            "file": test_dir / "alternative_format.txt",
            "expected": {
                "prescriber": "Dr. Maria Johansen",
                "medication": "Atorvastatin 20mg",
                "administration": "En tablett daglig, tas om kvelden"
            }
        },
        "Different Separators": {
            "file": test_dir / "different_separators.txt",
            "expected": {
                "prescriber": "Dr. Ingrid Bakke",
                "medication": "Sumatriptan",
                "administration": "En dose ved migreneanfall"
            }
        },
        "Missing Information": {
            "file": test_dir / "missing_info_format.txt",
            "expected": {
                "prescriber": None,
                "medication": "Metformin 850mg",
                "administration": "1 tablett 2 ganger daglig med måltid"
            }
        },
        "OCR Errors": {
            "file": test_dir / "ocr_errors_format.txt",
            "expected": {
                "prescriber": "Dr. Per Olav Pedersen",
                "medication": "Amlodipin 10mg tabletter",
                "administration": "1 tablett daglig, helst om morgenen"
            }
        }
    }
    
    # Prepare to collect results for evaluation
    all_results = []
    
    # Process each file test case
    print("\nTESTING FILE-BASED FORMATS:")
    for format_name, test_info in file_test_cases.items():
        logger.info(f"Testing {format_name} from {test_info['file']}")
        
        # Load test data
        text = load_test_data(test_info['file'])
        if not text:
            logger.error(f"Failed to load test data for {format_name}")
            continue
        
        # Analyze text
        try:
            results = analyzer.get_structured_data(text)
            print_analysis_results(format_name, text, results, test_info['expected'])
            
            # Collect results for evaluation
            prescriber = results.get('prescriber', {}).get('value') if isinstance(results.get('prescriber'), dict) else results.get('prescriber')
            medication = results.get('medication', {}).get('value') if isinstance(results.get('medication'), dict) else results.get('medication')
            administration = results.get('administration', {}).get('value') if isinstance(results.get('administration'), dict) else results.get('administration')
            
            all_results.append({
                'format': format_name,
                'prescriber_found': bool(prescriber),
                'medication_found': bool(medication),
                'administration_found': bool(administration)
            })
            
            # Log results
            logger.info(f"Analysis completed for {format_name}")
        except Exception as e:
            logger.error(f"Error analyzing {format_name}: {e}")
            print(f"Error analyzing {format_name}: {e}")
    
    # Process each custom test case
    print("\nTESTING CUSTOM FORMATS:")
    for test_case in CUSTOM_TEST_CASES:
        format_name = test_case['name']
        text = test_case['text']
        logger.info(f"Testing custom format: {format_name}")
        
        # Analyze text
        try:
            results = analyzer.get_structured_data(text)
            print_analysis_results(format_name, text, results)
            
            # Collect results for evaluation
            prescriber = results.get('prescriber', {}).get('value') if isinstance(results.get('prescriber'), dict) else results.get('prescriber')
            medication = results.get('medication', {}).get('value') if isinstance(results.get('medication'), dict) else results.get('medication')
            administration = results.get('administration', {}).get('value') if isinstance(results.get('administration'), dict) else results.get('administration')
            
            all_results.append({
                'format': format_name,
                'prescriber_found': bool(prescriber),
                'medication_found': bool(medication),
                'administration_found': bool(administration)
            })
            
            # Log results
            logger.info(f"Analysis completed for custom format: {format_name}")
        except Exception as e:
            logger.error(f"Error analyzing custom format {format_name}: {e}")
            print(f"Error analyzing custom format {format_name}: {e}")
    
    # Evaluate overall performance
    evaluate_analyzer_performance(all_results, len(file_test_cases) + len(CUSTOM_TEST_CASES))
    
    # Save results to JSON file for further analysis
    try:
        with open('format_test_results.json', 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2)
        print("\nDetailed results saved to format_test_results.json")
    except Exception as e:
        logger.error(f"Error saving results to JSON: {e}")
    
    print("\nSee comprehensive_test_results.log for detailed logging information")

if __name__ == "__main__":
    main()
