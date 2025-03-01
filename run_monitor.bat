@echo off
REM This script runs the clipboard monitor with the med_text_env conda environment
REM It is used by the start_clipboard_service.ps1 script

REM Set environment variables
set CONDA_ENV_PATH=d:\Conda.env\med_text_env
set SCRIPT_PATH=%~dp0clipboard_monitor.py

REM Echo environment info for debugging
echo Using conda environment: %CONDA_ENV_PATH%
echo Running script: %SCRIPT_PATH%

REM Activate the conda environment using full path to avoid PATH issues
call d:\Conda.env\med_text_env\Scripts\activate.bat

REM Verify we're in the right environment
echo Current Python: 
where python

REM Run the clipboard monitor
echo Running clipboard monitor with med_text_env environment...
python "%SCRIPT_PATH%"
