@echo off
echo Starting Medical Text Extractor Clipboard Monitor Service
echo ======================================================

REM Activate conda environment
echo Activating med_text_env conda environment...
call conda activate d:\Conda.env\med_text_env
if %ERRORLEVEL% NEQ 0 (
    echo Failed to activate conda environment.
    echo Make sure the environment exists at d:\Conda.env\med_text_env
    exit /b 1
)

REM Check if required packages are installed
echo Checking for required packages...
python -c "import sys; packages = ['opencv-python', 'pillow', 'pyautogui', 'pynput', 'pyperclip', 'pytesseract', 'win10toast']; missing = [p for p in packages if p.replace('-', '_').split('==')[0] not in [pkg.key for pkg in __import__('pkg_resources').working_set]]; sys.exit(1 if missing else 0)"
if %ERRORLEVEL% NEQ 0 (
    echo Some required packages are missing. Installing them now...
    pip install opencv-python pillow pyautogui pynput pyperclip pytesseract win10toast
)

REM Start the clipboard monitor
echo Starting clipboard monitor in background...
start /B pythonw "%~dp0clipboard_monitor.py"

echo Service started successfully.
echo To check service status, run: check_clipboard_service.ps1
echo To stop the service, run: stop_clipboard_service.ps1
