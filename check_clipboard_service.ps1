# PowerShell script to check the status of the clipboard monitor service
# This script checks if the clipboard monitor is running

# Define conda environment
$condaEnvPath = "d:\Conda.env\med_text_env"

# Function to check if the monitor is running
function IsMonitorRunning {
    $processName = "python"
    $processes = Get-Process -Name $processName -ErrorAction SilentlyContinue
    
    foreach ($process in $processes) {
        try {
            $cmdLine = (Get-WmiObject Win32_Process -Filter "ProcessId = $($process.Id)").CommandLine
            if ($cmdLine -like "*clipboard_monitor.py*") {
                # Get the parent process to check if it was launched by conda
                $parentPid = (Get-WmiObject Win32_Process -Filter "ProcessId = $($process.Id)").ParentProcessId
                $parentCmdLine = (Get-WmiObject Win32_Process -Filter "ProcessId = $parentPid").CommandLine
                
                return @{
                    Running = $true
                    PID = $process.Id
                    StartTime = $process.StartTime
                    RunningTime = (Get-Date) - $process.StartTime
                    CommandLine = $cmdLine
                    ParentPID = $parentPid
                    ParentCommandLine = $parentCmdLine
                }
            }
        } catch {
            Write-Warning "Error checking process $($process.Id): $_"
        }
    }
    
    return @{ Running = $false }
}

# Check if the monitor is running
$status = IsMonitorRunning

if ($status.Running) {
    Write-Host "Clipboard Monitor Service Status: RUNNING" -ForegroundColor Green
    Write-Host "Process ID: $($status.PID)" -ForegroundColor White
    Write-Host "Started: $($status.StartTime)" -ForegroundColor White
    Write-Host "Running Time: $($status.RunningTime)" -ForegroundColor White
    Write-Host "Command Line: $($status.CommandLine)" -ForegroundColor White
    
    # Check if using the correct conda environment
    $usingCorrectEnv = $false
    
    # Check command line for environment indicators
    if ($status.CommandLine -like "*$condaEnvPath*" -or 
        $status.ParentCommandLine -like "*$condaEnvPath*" -or 
        $status.CommandLine -like "*med_text_env*" -or 
        $status.ParentCommandLine -like "*med_text_env*") {
        $usingCorrectEnv = $true
    }
    
    if ($usingCorrectEnv) {
        Write-Host "Using correct conda environment: med_text_env" -ForegroundColor Green
    } else {
        Write-Host "WARNING: May not be using the correct conda environment (med_text_env)" -ForegroundColor Yellow
        Write-Host "To restart with the correct environment, run:" -ForegroundColor Yellow
        Write-Host "  .\Restart-ClipboardMonitor.ps1" -ForegroundColor White
    }
    
    # Check if log file exists and show last few entries
    $logPath = Join-Path -Path $PSScriptRoot -ChildPath "clipboard_monitor.log"
    if (Test-Path $logPath) {
        Write-Host "`nRecent log entries:" -ForegroundColor Cyan
        Write-Host "-----------------" -ForegroundColor Cyan
        Get-Content -Path $logPath -Tail 5
    }
    
    exit 0
} else {
    Write-Host "Clipboard Monitor Service Status: NOT RUNNING" -ForegroundColor Red
    Write-Host "To start the service, run:" -ForegroundColor Yellow
    Write-Host "  .\Restart-ClipboardMonitor.ps1" -ForegroundColor White
    exit 1
}
