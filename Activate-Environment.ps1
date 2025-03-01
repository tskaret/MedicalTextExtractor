# PowerShell script to activate the med_text_env conda environment
# This script activates the environment and opens a new PowerShell window with the environment active

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
    exit 1
}

Write-Host "Activating med_text_env conda environment..." -ForegroundColor Green

# Create a temporary script that will be executed in the new PowerShell window
$tempScriptPath = [System.IO.Path]::GetTempFileName() + ".ps1"
@"
# Initialize conda for PowerShell
`$env:CONDA_EXE = (Get-Command conda).Source
`$condaModulePath = (Get-ChildItem -Path (Split-Path `$env:CONDA_EXE) -Filter "conda.psm1" -Recurse).FullName
if (`$condaModulePath) {
    Import-Module `$condaModulePath
}

# Activate the environment
conda activate "$condaEnvPath"

# Set the window title
`$host.UI.RawUI.WindowTitle = "Medical Text Extractor - med_text_env"

# Display information
Write-Host "Medical Text Extractor Environment" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""
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

# Keep the window open
"@ | Out-File -FilePath $tempScriptPath -Encoding utf8

# Start a new PowerShell window with the temporary script
Start-Process powershell.exe -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-File", "`"$tempScriptPath`""

# Display success message in the current window
Write-Host "A new PowerShell window has been opened with the med_text_env environment activated." -ForegroundColor Green
Write-Host "You can close this window." -ForegroundColor Gray
