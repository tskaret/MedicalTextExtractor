@echo off
echo Starting Medical Text Extractor Enhanced Clipboard Monitor...
echo Using conda environment: d:\Conda.env\med_text_env
echo Running script: c:\Users\torgn\MedicalTextExtractor\enhanced_clipboard_monitor.py

REM Activate conda environment and run the script
call d:\Conda.env\med_text_env\Scripts\activate.bat
python "c:\Users\torgn\MedicalTextExtractor\enhanced_clipboard_monitor.py"
