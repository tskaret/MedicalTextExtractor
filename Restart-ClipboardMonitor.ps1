# PowerShell script to start/restart the clipboard monitor with the correct conda environment
# This script will stop any existing monitor process before starting a new one

# Define environment variables
$condaEnvPath = "d:\Conda.env\med_text_env"
$scriptPath = Join-Path -Path $PSScriptRoot -ChildPath "clipboard_monitor.py"

# Check if the script exists
if (-not (Test-Path $scriptPath)) {
    Write-Host "Error: Clipboard monitor script not found at $scriptPath" -ForegroundColor Red
    exit 1
}

# Check if the conda environment exists
if (-not (Test-Path $condaEnvPath)) {
    Write-Host "Error: Conda environment not found at $condaEnvPath" -ForegroundColor Red
    exit 1
}

# Function to stop any running monitor processes
function Stop-ClipboardMonitor {
    $processName = "python"
    $processes = Get-Process -Name $processName -ErrorAction SilentlyContinue
    $monitorStopped = $false
    
    foreach ($process in $processes) {
        try {
            $cmdLine = (Get-WmiObject Win32_Process -Filter "ProcessId = $($process.Id)").CommandLine
            if ($cmdLine -like "*clipboard_monitor.py*") {
                Write-Host "Stopping clipboard monitor process (PID: $($process.Id))..." -ForegroundColor Yellow
                Stop-Process -Id $process.Id -Force
                $monitorStopped = $true
            }
        } catch {
            Write-Warning "Error stopping process $($process.Id): $_"
        }
    }
    
    if ($monitorStopped) {
        Write-Host "Clipboard monitor service stopped successfully." -ForegroundColor Green
        # Wait a moment to ensure process is fully stopped
        Start-Sleep -Seconds 1
    } else {
        Write-Host "No running clipboard monitor service found." -ForegroundColor Cyan
    }
}

# First, stop any running instances
Stop-ClipboardMonitor

# Create a temporary batch file to run the monitor
$tempBatchFile = [System.IO.Path]::GetTempFileName() + ".bat"
@"
@echo off
echo Starting Medical Text Extractor Clipboard Monitor...
echo Using conda environment: $condaEnvPath
echo Running script: $scriptPath

REM Use conda directly to run the script in the environment
conda run -p "$condaEnvPath" python "$scriptPath"
"@ | Out-File -FilePath $tempBatchFile -Encoding ascii

Write-Host "Starting clipboard monitor service..." -ForegroundColor Cyan
try {
    # Start the process hidden
    Start-Process -FilePath "cmd.exe" -ArgumentList "/c", "`"$tempBatchFile`"" -WindowStyle Hidden
    
    # Wait a moment for the process to start
    Start-Sleep -Seconds 2
    
    # Check if the process is running
    $isRunning = $false
    $processName = "python"
    $processes = Get-Process -Name $processName -ErrorAction SilentlyContinue
    foreach ($process in $processes) {
        try {
            $cmdLine = (Get-WmiObject Win32_Process -Filter "ProcessId = $($process.Id)").CommandLine
            if ($cmdLine -like "*clipboard_monitor.py*") {
                $isRunning = $true
                $pid = $process.Id
                break
            }
        } catch {
            Write-Warning "Error checking process $($process.Id): $_"
        }
    }
    
    if ($isRunning) {
        Write-Host "Clipboard monitor service started successfully (PID: $pid)" -ForegroundColor Green
        
        # Create a toast notification
        Add-Type -AssemblyName System.Windows.Forms
        $notification = New-Object System.Windows.Forms.NotifyIcon
        $notification.Icon = [System.Drawing.SystemIcons]::Information
        $notification.BalloonTipTitle = "Medical Text Extractor"
        $notification.BalloonTipText = "Clipboard monitor service is now running."
        $notification.Visible = $true
        $notification.ShowBalloonTip(5000)
        
        # Clean up the temporary batch file
        Remove-Item -Path $tempBatchFile -Force
        
        # Run check service to show more details
        & "$PSScriptRoot\check_clipboard_service.ps1"
    } else {
        Write-Host "Failed to start clipboard monitor service." -ForegroundColor Red
        Write-Host "Try running the monitor directly with:" -ForegroundColor Yellow
        Write-Host "  conda run -p $condaEnvPath python $scriptPath" -ForegroundColor White
        
        # Keep the batch file for debugging
        Write-Host "Temporary batch file created at: $tempBatchFile" -ForegroundColor Gray
    }
} catch {
    Write-Host "Error starting clipboard monitor: $_" -ForegroundColor Red
    exit 1
}
