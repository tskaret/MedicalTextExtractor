# PowerShell script to set up the conda environment for Medical Text Extractor
# This script creates and configures the med_text_env conda environment

# Define environment variables
$condaEnvName = "med_text_env"
$condaEnvPath = "d:\Conda.env\med_text_env"
$pythonVersion = "3.9"

# Check if conda is available
try {
    $condaInfo = conda info --json | ConvertFrom-Json
    Write-Host "Conda is available. Conda version: $($condaInfo.conda_version)"
} catch {
    Write-Error "Conda is not available. Please install Anaconda or Miniconda and try again."
    exit 1
}

# Check if the environment already exists
$envExists = $false
$envs = conda env list --json | ConvertFrom-Json
foreach ($env in $envs.envs) {
    if ($env -eq $condaEnvPath -or $env -like "*\$condaEnvName") {
        $envExists = $true
        break
    }
}

if ($envExists) {
    Write-Host "Conda environment '$condaEnvName' already exists."
    
    # Ask if user wants to update the environment
    $updateEnv = Read-Host "Do you want to update the environment with required packages? (y/n)"
    if ($updateEnv -ne "y") {
        Write-Host "Environment update skipped."
        exit 0
    }
} else {
    # Create the conda environment
    Write-Host "Creating conda environment '$condaEnvName' with Python $pythonVersion..."
    conda create -y -p $condaEnvPath python=$pythonVersion
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to create conda environment."
        exit 1
    }
    
    Write-Host "Conda environment created successfully."
}

# Install required packages
Write-Host "Installing required packages in the conda environment..."

# Create a batch file to activate conda and install packages
$batchFile = Join-Path -Path $PSScriptRoot -ChildPath "install_packages_temp.bat"
@"
@echo off
call conda activate $condaEnvPath
pip install opencv-python pillow pyautogui pynput pyperclip pytesseract win10toast
"@ | Out-File -FilePath $batchFile -Encoding ascii

# Run the batch file
Write-Host "Installing packages..."
Start-Process -FilePath "cmd.exe" -ArgumentList "/c $batchFile" -NoNewWindow -Wait

# Clean up the temporary batch file
if (Test-Path $batchFile) {
    Remove-Item $batchFile -Force
}

Write-Host "Package installation completed."

# Create a batch file to activate the environment
$activateScript = Join-Path -Path $PSScriptRoot -ChildPath "activate_env.bat"
@"
@echo off
call conda activate $condaEnvPath
cmd /k
"@ | Out-File -FilePath $activateScript -Encoding ascii

Write-Host "Environment setup completed."
Write-Host "To activate the environment, run: .\activate_env.bat"
