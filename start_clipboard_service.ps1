# PowerShell script to start the clipboard monitor service
# This script starts the clipboard monitor in a hidden window

# Define conda environment
$condaEnvPath = "d:\Conda.env\med_text_env"
$scriptDir = $PSScriptRoot

# Check if the monitor is already running
$monitorRunning = $false
$processName = "python"
$processes = Get-Process -Name $processName -ErrorAction SilentlyContinue

foreach ($process in $processes) {
    try {
        $cmdLine = (Get-WmiObject Win32_Process -Filter "ProcessId = $($process.Id)").CommandLine
        if ($cmdLine -like "*clipboard_monitor.py*") {
            $monitorRunning = $true
            $monitorPid = $process.Id
            break
        }
    } catch {
        Write-Warning "Error checking process $($process.Id): $_"
    }
}

if ($monitorRunning) {
    Write-Host "Clipboard monitor is already running (PID: $monitorPid)" -ForegroundColor Yellow
    Write-Host "To restart, first run: .\stop_clipboard_service.ps1" -ForegroundColor Cyan
    exit 0
}

# Ensure the run_monitor.bat file exists
$batchFile = Join-Path -Path $scriptDir -ChildPath "run_monitor.bat"
if (-not (Test-Path $batchFile)) {
    Write-Host "Error: run_monitor.bat not found at $batchFile" -ForegroundColor Red
    exit 1
}

# Start the monitor using the batch file
Write-Host "Starting clipboard monitor service..." -ForegroundColor Cyan
try {
    # Start the process hidden
    Start-Process -FilePath "cmd.exe" -ArgumentList "/c", "`"$batchFile`"" -WindowStyle Hidden
    
    # Wait a moment for the process to start
    Start-Sleep -Seconds 2
    
    # Check if the process is running
    $isRunning = $false
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
        
        # Run check service to show more details
        & "$scriptDir\check_clipboard_service.ps1"
    } else {
        Write-Host "Failed to start clipboard monitor service." -ForegroundColor Red
        Write-Host "Try running the monitor directly with:" -ForegroundColor Yellow
        Write-Host "  . .\Activate-CurrentSession.ps1" -ForegroundColor White
        Write-Host "  python clipboard_monitor.py" -ForegroundColor White
    }
} catch {
    Write-Host "Error starting clipboard monitor: $_" -ForegroundColor Red
    exit 1
}
