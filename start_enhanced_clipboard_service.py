#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Start Enhanced Clipboard Service - Script to start the enhanced clipboard monitor service
with system tray icon using the correct conda environment.
"""

import os
import sys
import subprocess
import time
import logging
from pathlib import Path
import ctypes
import win32api
import win32con

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('service_starter.log')
    ]
)
logger = logging.getLogger("ServiceStarter")

# Constants
CONDA_ENV_PATH = r"d:\Conda.env\med_text_env"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MONITOR_SCRIPT = os.path.join(SCRIPT_DIR, "enhanced_clipboard_monitor.py")
BATCH_FILE = os.path.join(SCRIPT_DIR, "run_enhanced_monitor.bat")

def show_message(title, message, is_error=False):
    """Show a message box with the given title and message."""
    icon = win32con.MB_ICONERROR if is_error else win32con.MB_ICONINFORMATION
    win32api.MessageBox(0, message, title, win32con.MB_OK | icon)

def is_monitor_running():
    """Check if the enhanced clipboard monitor is already running."""
    try:
        # Use PowerShell to find processes running the enhanced_clipboard_monitor.py script
        powershell_cmd = (
            "Get-Process -Name python -ErrorAction SilentlyContinue | "
            "ForEach-Object { "
            "   $cmdLine = (Get-WmiObject Win32_Process -Filter \"ProcessId = $($_.Id)\").CommandLine; "
            "   if ($cmdLine -like '*enhanced_clipboard_monitor.py*') { "
            "       [PSCustomObject]@{ ProcessId = $_.Id; CommandLine = $cmdLine } "
            "   } "
            "}"
        )
        
        result = subprocess.run(
            ["powershell", "-Command", powershell_cmd],
            capture_output=True,
            text=True,
            check=False
        )
        
        # Check if any processes were found
        if result.stdout.strip():
            # Extract the process ID from the output
            import re
            match = re.search(r"ProcessId\s*:\s*(\d+)", result.stdout)
            if match:
                return int(match.group(1))
            return True  # Process is running but couldn't get PID
        
        return False  # No process found
    
    except Exception as e:
        logger.error(f"Error checking if monitor is running: {e}")
        return False

def create_batch_file():
    """Create the batch file to run the enhanced clipboard monitor."""
    try:
        # Create the batch file content
        batch_content = f"""@echo off
echo Starting Medical Text Extractor Enhanced Clipboard Monitor...
echo Using conda environment: {CONDA_ENV_PATH}
echo Running script: {MONITOR_SCRIPT}

REM Activate conda environment and run the script
call {os.path.join(CONDA_ENV_PATH, 'Scripts', 'activate.bat')}
python "{MONITOR_SCRIPT}"
"""
        
        # Write the batch file
        with open(BATCH_FILE, "w") as f:
            f.write(batch_content)
        
        logger.info(f"Created batch file: {BATCH_FILE}")
        return True
    
    except Exception as e:
        logger.error(f"Error creating batch file: {e}")
        return False

def start_monitor():
    """Start the enhanced clipboard monitor service."""
    try:
        # Check if the monitor script exists
        if not os.path.exists(MONITOR_SCRIPT):
            error_msg = f"Enhanced clipboard monitor script not found: {MONITOR_SCRIPT}"
            logger.error(error_msg)
            show_message("Error", error_msg, is_error=True)
            return False
        
        # Check if the conda environment exists
        if not os.path.exists(CONDA_ENV_PATH):
            error_msg = f"Conda environment not found: {CONDA_ENV_PATH}"
            logger.error(error_msg)
            show_message("Error", error_msg, is_error=True)
            return False
        
        # Create the batch file
        if not create_batch_file():
            error_msg = "Failed to create batch file"
            logger.error(error_msg)
            show_message("Error", error_msg, is_error=True)
            return False
        
        # Start the process hidden
        logger.info("Starting enhanced clipboard monitor service...")
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = 0  # SW_HIDE
        
        process = subprocess.Popen(
            ["cmd.exe", "/c", BATCH_FILE],
            startupinfo=startupinfo,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        
        # Wait a moment for the process to start
        time.sleep(3)
        
        # Check if the process is running
        pid = is_monitor_running()
        if pid:
            success_msg = f"Enhanced clipboard monitor service started successfully (PID: {pid})"
            logger.info(success_msg)
            show_message("Success", success_msg)
            return True
        else:
            error_msg = "Failed to start enhanced clipboard monitor service"
            logger.error(error_msg)
            show_message("Error", error_msg, is_error=True)
            return False
    
    except Exception as e:
        error_msg = f"Error starting enhanced clipboard monitor: {e}"
        logger.error(error_msg)
        show_message("Error", error_msg, is_error=True)
        return False

def main():
    """Main function to start the enhanced clipboard monitor service."""
    logger.info("Starting enhanced clipboard monitor service...")
    
    # Check if the monitor is already running
    pid = is_monitor_running()
    if pid:
        msg = f"Enhanced clipboard monitor is already running (PID: {pid})"
        logger.warning(msg)
        show_message("Already Running", msg)
        return
    
    # Start the monitor
    start_monitor()

if __name__ == "__main__":
    main()
