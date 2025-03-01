# PowerShell script to activate the med_text_env conda environment
# This script will activate the environment and then start a new PowerShell session

Write-Host "Activating med_text_env conda environment..." -ForegroundColor Green

# Get the conda installation path
$condaPath = (Get-Command conda -ErrorAction SilentlyContinue).Source
if (-not $condaPath) {
    Write-Host "Conda not found in PATH. Trying common installation locations..." -ForegroundColor Yellow
    
    # Check common installation paths
    $commonPaths = @(
        "C:\ProgramData\Miniconda3\Scripts\conda.exe",
        "C:\ProgramData\Anaconda3\Scripts\conda.exe",
        "C:\Users\$env:USERNAME\Miniconda3\Scripts\conda.exe",
        "C:\Users\$env:USERNAME\Anaconda3\Scripts\conda.exe"
    )
    
    foreach ($path in $commonPaths) {
        if (Test-Path $path) {
            $condaPath = $path
            break
        }
    }
}

if (-not $condaPath) {
    Write-Host "Error: Could not find conda installation. Please make sure conda is installed and in your PATH." -ForegroundColor Red
    exit 1
}

Write-Host "Found conda at: $condaPath" -ForegroundColor Green

# Get the conda base directory
$condaBaseDir = Split-Path -Parent (Split-Path -Parent $condaPath)
Write-Host "Conda base directory: $condaBaseDir" -ForegroundColor Green

# Initialize conda for PowerShell
Write-Host "Initializing conda for PowerShell..." -ForegroundColor Green
& "$condaBaseDir\Scripts\activate.ps1"

# Activate the med_text_env environment
Write-Host "Activating med_text_env environment..." -ForegroundColor Green
conda activate med_text_env

# Verify the environment is activated
$currentEnv = & conda info --envs | Select-String -Pattern "\*" | ForEach-Object { $_.ToString().Trim() }
Write-Host "Current environment: $currentEnv" -ForegroundColor Green

# Start a new PowerShell session with the environment activated
Write-Host "Starting a new PowerShell session with med_text_env activated..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; conda activate med_text_env; Write-Host 'med_text_env activated!' -ForegroundColor Green"

Write-Host "Done! A new PowerShell window should have opened with the med_text_env environment activated." -ForegroundColor Green
