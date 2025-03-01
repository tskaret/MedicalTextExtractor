# PowerShell script to activate the med_text_env conda environment in the current session
# This script must be "dot-sourced" to affect the current session
# Usage: . .\Activate-CurrentSession.ps1

# Define environment variables
$condaEnvPath = "d:\Conda.env\med_text_env"

# Display header
Write-Host "Medical Text Extractor - Environment Activation" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Check if the environment exists
if (-not (Test-Path $condaEnvPath)) {
    Write-Host "Error: Conda environment not found at $condaEnvPath" -ForegroundColor Red
    Write-Host "Please run setup_conda_env.ps1 first to create the environment." -ForegroundColor Yellow
    return
}

Write-Host "Activating med_text_env conda environment in current session..." -ForegroundColor Green

# Simple direct activation approach
try {
    # Try direct conda activation first (this usually works if conda is initialized)
    conda activate $condaEnvPath 2>$null
    
    # Check if activation was successful
    if ($LASTEXITCODE -eq 0 -or $?) {
        # Set the window title
        $host.UI.RawUI.WindowTitle = "Medical Text Extractor - med_text_env"
        
        # Display success information
        Write-Host ""
        Write-Host "Environment activated successfully!" -ForegroundColor Green
        Write-Host "Environment: med_text_env" -ForegroundColor Green
        Write-Host "Location: $condaEnvPath" -ForegroundColor Green
        Write-Host ""
        Write-Host "Available commands:" -ForegroundColor Yellow
        Write-Host "  python process_clipboard_image.py - Process an image from clipboard" -ForegroundColor White
        Write-Host "  python clipboard_monitor.py - Run the clipboard monitor" -ForegroundColor White
        Write-Host "  .\start_clipboard_service.ps1 - Start the clipboard monitor as a service" -ForegroundColor White
        Write-Host "  .\check_clipboard_service.ps1 - Check the status of the clipboard monitor service" -ForegroundColor White
        Write-Host "  .\stop_clipboard_service.ps1 - Stop the clipboard monitor service" -ForegroundColor White
        Write-Host ""
        return
    }
} catch {
    # If direct activation fails, we'll try alternative methods
    Write-Host "Direct conda activation failed. Trying alternative methods..." -ForegroundColor Yellow
}

# Try using conda init and then activate
try {
    Write-Host "Initializing conda for PowerShell..." -ForegroundColor Yellow
    conda init powershell 2>$null
    
    # Source the profile to get conda commands
    if (Test-Path $PROFILE) {
        . $PROFILE
    }
    
    # Try activation again
    conda activate $condaEnvPath
    
    # Set the window title
    $host.UI.RawUI.WindowTitle = "Medical Text Extractor - med_text_env"
    
    # Display success information
    Write-Host ""
    Write-Host "Environment activated successfully!" -ForegroundColor Green
    Write-Host "Environment: med_text_env" -ForegroundColor Green
    Write-Host "Location: $condaEnvPath" -ForegroundColor Green
    Write-Host ""
    Write-Host "Available commands:" -ForegroundColor Yellow
    Write-Host "  python process_clipboard_image.py - Process an image from clipboard" -ForegroundColor White
    Write-Host "  python clipboard_monitor.py - Run the clipboard monitor" -ForegroundColor White
    Write-Host "  .\start_clipboard_service.ps1 - Start the clipboard monitor as a service" -ForegroundColor White
    Write-Host "  .\check_clipboard_service.ps1 - Check the status of the clipboard monitor service" -ForegroundColor White
    Write-Host "  .\stop_clipboard_service.ps1 - Stop the clipboard monitor service" -ForegroundColor White
    Write-Host ""
} catch {
    Write-Host "Could not activate the conda environment. Please try running 'conda init powershell' manually and restart your PowerShell session." -ForegroundColor Red
}
