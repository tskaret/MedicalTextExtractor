# PowerShell script to stop the clipboard monitor service
# This script finds and terminates all instances of the clipboard monitor

# Function to find and stop clipboard monitor processes
function StopClipboardMonitor {
    $processName = "python"
    $processes = Get-Process -Name $processName -ErrorAction SilentlyContinue
    $monitorStopped = $false
    
    foreach ($process in $processes) {
        try {
            $cmdLine = (Get-WmiObject Win32_Process -Filter "ProcessId = $($process.Id)").CommandLine
            if ($cmdLine -like "*clipboard_monitor.py*") {
                Write-Host "Stopping clipboard monitor process (PID: $($process.Id))..."
                Stop-Process -Id $process.Id -Force
                $monitorStopped = $true
            }
        } catch {
            Write-Warning "Error checking process $($process.Id): $_"
        }
    }
    
    return $monitorStopped
}

# Stop the clipboard monitor
$stopped = StopClipboardMonitor

if ($stopped) {
    Write-Host "Clipboard monitor service stopped successfully."
    
    # Create a notification that the service has stopped
    Add-Type -AssemblyName System.Windows.Forms
    $global:balloon = New-Object System.Windows.Forms.NotifyIcon
    $path = (Get-Process -id $pid).Path
    $balloon.Icon = [System.Drawing.Icon]::ExtractAssociatedIcon($path)
    $balloon.BalloonTipIcon = [System.Windows.Forms.ToolTipIcon]::Info
    $balloon.BalloonTipTitle = "Medical Text Extractor"
    $balloon.BalloonTipText = "Clipboard monitor service stopped."
    $balloon.Visible = $true
    $balloon.ShowBalloonTip(5000)
} else {
    Write-Host "No running clipboard monitor service found."
}
