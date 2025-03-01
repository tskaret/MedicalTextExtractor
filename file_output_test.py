#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script that writes results to a file.
"""

import json
from text_analyzer import TextAnalyzer

def main():
    # Initialize text analyzer
    analyzer = TextAnalyzer()
    
    # Fosamax text to analyze
    fosamax_text = """Fosamax

Tabletten skal tas straks pasienten står opp om morgenen, sammen med et fullt glass vann på fastende mage, minst 1/2 time før inntak av annen drikke, mat eller andre legemidler. For å lette transporten til magen, og derved redusere risikoen for lokal og øsofageal irritasjon​/​bivirkning, skal pasienten sitte oppreist eller stå inntil dagens første måltid er inntatt (dvs. minst 1/2 time etter tablettinntak). Tabletten skal ikke tas ved sengetid eller før en står opp. Tabletten skal svelges hel. Skal ikke tygges, knuses eller oppløses i munnen.

doctor 10017852, Torgny Skaret"""
    
    # Analyze the text
    print("Analyzing Fosamax text...")
    results = analyzer.analyze_text(fosamax_text)
    
    # Write results to a file
    with open('fosamax_results.txt', 'w', encoding='utf-8') as f:
        f.write("Raw Results Dictionary:\n")
        f.write(json.dumps(results, indent=2, ensure_ascii=False))
        
        f.write("\n\nExtracted Information:\n")
        f.write(f"Prescriber: {results.get('prescriber', 'Not found')}\n")
        f.write(f"Medication: {results.get('medication', 'Not found')}\n")
        f.write(f"Administration: {results.get('administration', 'Not found')}\n")
    
    print("Results written to fosamax_results.txt")

if __name__ == "__main__":
    main()
