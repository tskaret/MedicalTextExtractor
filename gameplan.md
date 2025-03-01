# Medical Text Extractor - Project Game Plan

This document outlines the comprehensive project plan for the Medical Text Extractor application, which is designed to monitor screenshots, extract medical information using OCR, and provide easy access to medication administration instructions.

## Project Overview

The Medical Text Extractor is a background application that:
- Monitors for screenshots
- Uses OCR to extract text from images
- Identifies Norwegian medical terms such as "rekvirent" (prescriber) and "Legemiddel" (medication)
- Extracts and stores administration instructions
- Provides clipboard functionality to paste the extracted information

## Completed Tasks

### Environment Setup
- ✅ Created project directory: MedicalTextExtractor
- ✅ Created a dedicated conda virtual environment: med_text_env with Python 3.9
  - Environment location: d:\Conda.env\med_text_env
  - **Note: All scripts should be run using this environment**
- ✅ Installed required packages:
- opencv-python - for image processing
- pillow - for image manipulation
- pyautogui - for screenshot detection and automation
- pynput - for keyboard/mouse monitoring
- pyperclip - for clipboard operations
- pytesseract - Python wrapper for Tesseract OCR
- win10toast - for Windows toast notifications

### Core Components
- ✅ Created screenshot_monitor.py - Detects screenshots using keyboard monitoring
- ✅ Created ocr_processor.py - Extracts text from images using Tesseract OCR
- ✅ Created text_analyzer.py - Identifies medication information in extracted text
- ✅ Created database/db_manager.py - Stores and retrieves medication information
- ✅ Created clipboard_manager.py - Manages copying data to the clipboard
- ✅ Created main.py - Integrates all components and provides CLI interface

## Current Status

The application has a functional architecture with all major components implemented. The current implementation allows for:
- Background monitoring of screenshots
- OCR processing of captured images
- Text analysis to extract medication information
- Database storage of extracted information
- Clipboard functionality for copying information
- Command-line interface for basic interaction
- Direct processing of clipboard images
- Improved text analysis for various medication formats
- Lookup of medication administration instructions from the database
- Automatic clipboard monitoring for medication images
- Toast notifications for extracted medication information
- Service-like operation with PowerShell scripts for management

## Remaining Tasks

### 1. Integration and Bug Fixes
- ✅ Update the `clipboard_manager.py` interface to match what's used in `main.py`
- ✅ Ensure `TextAnalyzer.analyze()` method exists (currently we have `analyze_text()`)
- ✅ Update `DatabaseManager` to include the `store_medication_info()` and `search_medications()` methods 
- ✅ Implement the `close()` method in `DatabaseManager`

### 2. Configuration and Error Handling (Priority)
- ✅ Create a configuration system (config.py or settings.json)
- ✅ Enhance error handling throughout the application
- ✅ Improve logging configuration with rotation and appropriate log levels
- ✅ Create a separate schema.sql file for database initialization

### 3. System Integration and User Experience
- ✅ Add system tray integration for Windows
- ✅ Improve user feedback mechanisms
- ✅ Create a basic startup/shutdown service
- ✅ Add error notifications for the user

### 4. Text Analysis and Data Management
- ✅ Improve text analyzer to handle various medication information formats
- ✅ Implement preferred format for medication data extraction
- ✅ Create interface for manually adding medication data to the database
- ✅ Add utilities for viewing and managing stored medications
- ✅ Create clipboard image processing functionality
- ✅ Implement direct HPR number extraction
- ✅ Add automatic clipboard monitoring with toast notifications
- ✅ Implement service-like operation with PowerShell scripts

### 5. Testing
- ✅ Create unit tests for each component
- ✅ Perform end-to-end testing of the complete workflow
- ✅ Test with various medication information formats
- [ ] Performance testing under different conditions

### 6. Documentation
- [ ] Create comprehensive documentation:
- [ ] Installation guide
- [ ] User manual
- [ ] API documentation
- [ ] Troubleshooting section

### 7. Build and Deployment
- [ ] Create an installation script
- [ ] Bundle the application into a Windows executable
- [ ] Add auto-start functionality for system boot

## Future Enhancements

### 1. User Interface Improvements
- [ ] Develop a graphical user interface
- [ ] Create a history viewer for detected medications
- [ ] Add user preferences and customization options

### 2. Advanced Features
- [ ] Implement export functionality for various formats
- [ ] Add support for multiple languages beyond Norwegian
- [ ] Create cloud backup options for the database
- [ ] Implement advanced text recognition with AI/ML models
- [ ] Add support for PDF document analysis

### 3. Integration Possibilities
- [ ] Create plugins for electronic health record systems
- [ ] Develop mobile companion app
- [ ] Implement secure sharing of extracted information

## Project Structure

```
MedicalTextExtractor/
├── setup_env.ps1                # Environment setup script
├── setup_conda_env.ps1          # Conda environment setup script
├── activate_env.bat             # Script to activate conda environment
├── main.py                      # Application entry point
├── screenshot_monitor.py        # Screenshot detection module
├── ocr_processor.py             # OCR and text extraction
├── text_analyzer.py             # Logic to find medication info
├── improved_text_analyzer.py    # Enhanced version of text analyzer
├── clipboard_manager.py         # Copy/paste functionality
├── clipboard_monitor.py         # Monitor clipboard for medication images
├── process_clipboard_image.py   # Process images from clipboard
├── lookup_medication.py         # Look up medication in database
├── add_medication_improved.py   # Add medication data manually
├── test_preferred_format.py     # Test script for improved analyzer
├── view_medications.py          # View stored medications
├── start_clipboard_service.ps1  # Start clipboard monitor as a service
├── stop_clipboard_service.ps1   # Stop clipboard monitor service
├── check_clipboard_service.ps1  # Check status of clipboard monitor service
├── clipboard_service_readme.md  # Documentation for clipboard service
├── database/
│   ├── db_manager.py            # Database operations
│   └── schema.sql               # Database schema
├── config/
│   └── config.py                # Configuration settings
├── utils/
│   ├── logger.py                # Logging functionality
│   ├── error_handler.py         # Error handling functionality
│   ├── notifications.py         # User notification system
│   └── helpers.py               # Utility functions (to be created)
└── tests/                       # Unit tests
```

## External Requirements
- Tesseract OCR for Windows needs to be installed from: https://github.com/UB-Mannheim/tesseract/wiki
- Add Tesseract to system PATH after installation
- Conda environment med_text_env must be set up at d:\Conda.env\med_text_env
- The following packages must be installed in the conda environment:
  - opencv-python
  - pillow
  - pyautogui
  - pynput
  - pyperclip
  - pytesseract
  - win10toast

## Running the Application

### Environment Setup
```powershell
# Set up the conda environment (first time only)
powershell -ExecutionPolicy Bypass -File setup_conda_env.ps1

# Activate the conda environment
.\activate_env.bat
```

### Running the Clipboard Monitor Service
```powershell
# Start the service
.\start_clipboard_service.ps1

# Check service status
.\check_clipboard_service.ps1

# Stop the service
.\stop_clipboard_service.ps1
```

### Manual Processing
```powershell
# Process an image from clipboard
python process_clipboard_image.py

# Look up medication information
python lookup_medication.py [medication_name]

# View stored medications
python view_medications.py
```

## Timeline

- **Phase 1 (Completed)**: Core functionality implementation
- **Phase 2 (Completed)**: Integration fixes and component improvements
- **Phase 3 (Completed)**: Configuration, error handling and system integration
- **Phase 4 (Current)**: Testing, documentation, and deployment
- **Phase 5 (Future)**: UI improvements and advanced features

## Recent Achievements

### Clipboard Image Processing
- ✅ Created `process_clipboard_image.py` to extract medication information from clipboard images
- ✅ Implemented direct extraction of HPR numbers and medication names
- ✅ Added lookup functionality to retrieve administration instructions from the database
- ✅ Created `clipboard_monitor.py` to automatically detect and process clipboard images
- ✅ Added toast notifications for extracted medication information
- ✅ Implemented automatic copying of administration instructions to clipboard
- ✅ Created PowerShell scripts to run clipboard monitor as a background service

### Improved Text Analysis
- ✅ Enhanced the text analyzer to handle various formats including:
  - Standard format with "HPR-nr" and "Legemiddel" fields
  - Alternative format with "HPR:" and medication name on separate lines
- ✅ Improved pattern matching for more accurate extraction
- ✅ Added fallback mechanisms for different text formats

### Database Integration
- ✅ Created `lookup_medication.py` for easy retrieval of medication information
- ✅ Implemented search functionality to find medications by name
- ✅ Added display of administration instructions for found medications
- ✅ Added silent mode option for programmatic lookup

### Service Management
- ✅ Created PowerShell scripts for service-like operation:
  - `start_clipboard_service.ps1` - Start the monitor in the background
  - `stop_clipboard_service.ps1` - Stop all running monitor instances
  - `check_clipboard_service.ps1` - Check service status and view logs
- ✅ Added system notifications for service status changes
- ✅ Created comprehensive documentation for the service
