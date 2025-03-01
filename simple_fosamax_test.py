#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple test script for Fosamax format.
"""

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
    
    # Print results
    print("\nRaw Results Dictionary:")
    print(results)
    
    print("\nExtracted Information:")
    print(f"Prescriber: {results.get('prescriber', 'Not found')}")
    print(f"Medication: {results.get('medication', 'Not found')}")
    print(f"Administration: {results.get('administration', 'Not found')}")

if __name__ == "__main__":
    main()
