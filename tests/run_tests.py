#!/usr/bin/env python
"""
Test runner script for the Medical Text Extractor application.

This script discovers and runs all test files in the tests directory.
It uses Python's unittest discovery mechanism and provides a summary
of test results.
"""

import unittest
import sys
import os
import time
from datetime import datetime

def run_tests():
    """Run all tests in the tests directory and provide a summary of results."""
    # Get the directory of this script
    test_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Print header
    print("\n" + "=" * 70)
    print(f"RUNNING TESTS FOR MEDICAL TEXT EXTRACTOR")
    print(f"Date and Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70 + "\n")
    
    # Start timing
    start_time = time.time()
    
    # Create a test suite that discovers all test files in the tests directory
    test_suite = unittest.defaultTestLoader.discover(
        start_dir=test_dir,
        pattern='test_*.py'
    )
    
    # Create a test runner that will output results to the console
    test_runner = unittest.TextTestRunner(verbosity=2)
    
    # Run the tests and get the results
    result = test_runner.run(test_suite)
    
    # Calculate the elapsed time
    elapsed_time = time.time() - start_time
    
    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Ran {result.testsRun} tests in {elapsed_time:.2f} seconds")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    
    if result.failures:
        print(f"Failures: {len(result.failures)}")
        
    if result.errors:
        print(f"Errors: {len(result.errors)}")
        
    if result.skipped:
        print(f"Skipped: {len(result.skipped)}")
        
    # Return appropriate exit code
    return 0 if result.wasSuccessful() else 1

if __name__ == "__main__":
    sys.exit(run_tests())

