# Medical Text Extractor Service Management

This document explains how to manage the clipboard monitor service for the Medical Text Extractor application.

## Service Management Scripts

### Main Scripts

- `Restart-ClipboardMonitor.ps1` - Stops any running clipboard monitor service and starts a new one
- `check_clipboard_service.ps1` - Checks if the clipboard monitor service is running

### Environment Management

- `Activate-CurrentSession.ps1` - Activates the conda environment in the current PowerShell session
  - Must be dot-sourced: `. .\Activate-CurrentSession.ps1`
- `activate_env.bat` - Activates the conda environment in a cmd.exe session

## Usage Instructions

### Starting or Restarting the Service

To start or restart the clipboard monitor service:

```powershell
.\Restart-ClipboardMonitor.ps1
```

This will:
1. Stop any running clipboard monitor processes
2. Start a new clipboard monitor process using the correct conda environment
3. Verify the service is running properly
4. Display a toast notification

### Checking Service Status

To check if the clipboard monitor service is running:

```powershell
.\check_clipboard_service.ps1
```

This will display:
- Whether the service is running
- Process ID and start time
- Whether it's using the correct conda environment
- Recent log entries (if available)

### Activating the Environment for Development

If you want to activate the conda environment for development:

```powershell
# In PowerShell:
. .\Activate-CurrentSession.ps1

# In cmd.exe:
activate_env.bat
```

## Conda Environment

The Medical Text Extractor project uses a conda environment located at:
```
d:\Conda.env\med_text_env
```

This environment includes the following packages:
- opencv-python - for image processing
- pillow - for image manipulation
- pyautogui - for screenshot detection and automation
- pynput - for keyboard/mouse monitoring
- pyperclip - for clipboard operations
- pytesseract - Python wrapper for Tesseract OCR
- win10toast - for Windows toast notifications
