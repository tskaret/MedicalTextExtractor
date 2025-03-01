# PowerShell script to activate the med_text_env conda environment
Write-Host "Activating med_text_env conda environment..." -ForegroundColor Green

# Specify the conda environment path
$condaEnvPath = "d:\Conda.env\med_text_env"

# Check if the environment exists
if (-not (Test-Path $condaEnvPath)) {
    Write-Host "Error: Conda environment not found at $condaEnvPath" -ForegroundColor Red
    exit 1
}

Write-Host "Found conda environment at: $condaEnvPath" -ForegroundColor Green

# Create a batch file to activate the environment and start a new PowerShell session
$batchContent = @"
@echo off
call activate med_text_env
powershell
"@

$batchFile = Join-Path -Path $PWD -ChildPath "temp_activate.bat"
$batchContent | Out-File -FilePath $batchFile -Encoding ASCII

Write-Host "Starting a new PowerShell session with med_text_env activated..." -ForegroundColor Green
Write-Host "Please run your commands in the new window that will open." -ForegroundColor Yellow

# Start the batch file
Start-Process -FilePath $batchFile -NoNewWindow

Write-Host "Done! A new window should have opened with the med_text_env environment activated." -ForegroundColor Green
