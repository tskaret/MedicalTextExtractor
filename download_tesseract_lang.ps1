# PowerShell script to download Tesseract language data

Write-Host "Downloading Tesseract language data..." -ForegroundColor Green

# Define the Tesseract installation path
$tesseractPath = "C:\Program Files\Tesseract-OCR"
if (-not (Test-Path $tesseractPath)) {
    $tesseractPath = "C:\Program Files (x86)\Tesseract-OCR"
}

if (-not (Test-Path $tesseractPath)) {
    Write-Host "Tesseract OCR not found. Please install it first." -ForegroundColor Red
    exit 1
}

Write-Host "Tesseract OCR found at: $tesseractPath" -ForegroundColor Green

# Create tessdata directory if it doesn't exist
$tessdataPath = Join-Path -Path $tesseractPath -ChildPath "tessdata"
if (-not (Test-Path $tessdataPath)) {
    New-Item -Path $tessdataPath -ItemType Directory | Out-Null
    Write-Host "Created tessdata directory: $tessdataPath" -ForegroundColor Green
}

# Define the languages to download
$languages = @("eng", "nor")

# GitHub URL for tessdata
$baseUrl = "https://github.com/tesseract-ocr/tessdata/raw/main"

# Download each language file
foreach ($lang in $languages) {
    $langFile = "$lang.traineddata"
    $outputFile = Join-Path -Path $tessdataPath -ChildPath $langFile
    $url = "$baseUrl/$langFile"
    
    Write-Host "Downloading $langFile..." -ForegroundColor Yellow
    
    try {
        Invoke-WebRequest -Uri $url -OutFile $outputFile
        Write-Host "Successfully downloaded $langFile" -ForegroundColor Green
    }
    catch {
        Write-Host "Error downloading $langFile: $_" -ForegroundColor Red
    }
}

Write-Host "Download complete!" -ForegroundColor Green
Write-Host "Please restart the clipboard monitor service for the changes to take effect." -ForegroundColor Yellow
