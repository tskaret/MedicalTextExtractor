# Script to set up the environment for Medical Text Extractor

# Define the environment name
$envName = "med_text_env"

Write-Host "Activating conda environment: $envName" -ForegroundColor Green

# Activate conda environment
& "C:\Users\torgn\miniconda3\Scripts\activate.bat" $envName

Write-Host "Installing required packages..." -ForegroundColor Green

# Install required packages
pip install opencv-python pillow pyautogui pynput pyperclip pytesseract

# Check if installation was successful
if ($LASTEXITCODE -eq 0) {
    Write-Host "Successfully installed packages!" -ForegroundColor Green
} else {
    Write-Host "Error installing packages." -ForegroundColor Red
}

Write-Host "IMPORTANT NOTE:" -ForegroundColor Yellow
Write-Host "For pytesseract to work, you need to install Tesseract OCR separately:" -ForegroundColor Yellow
Write-Host "1. Download Tesseract OCR for Windows from: https://github.com/UB-Mannheim/tesseract/wiki" -ForegroundColor Yellow
Write-Host "2. Install it with default settings" -ForegroundColor Yellow
Write-Host "3. Add the Tesseract installation directory to your PATH" -ForegroundColor Yellow

Write-Host "Your environment is now ready!" -ForegroundColor Green

