# Clipboard Monitor Service

This service monitors your clipboard for images containing medication information, extracts the relevant details, and provides administration instructions.

## Features

- **Automatic Monitoring**: Continuously monitors the clipboard for new images
- **Medication Information Extraction**: Identifies HPR numbers and medication names
- **Database Integration**: Looks up administration instructions in the database
- **Clipboard Management**: Automatically copies administration instructions to the clipboard
- **Toast Notifications**: Displays Windows notifications with extracted information

## Service Management

The clipboard monitor can be run as a background service using the provided PowerShell scripts:

### Starting the Service

Run the following command in PowerShell:

```powershell
.\start_clipboard_service.ps1
```

This will start the clipboard monitor in the background. A notification will appear confirming that the service has started.

### Checking Service Status

To check if the service is running:

```powershell
.\check_clipboard_service.ps1
```

This will display information about the running service, including:
- Process ID
- Start time
- Running time
- Recent log entries

### Stopping the Service

To stop the clipboard monitor service:

```powershell
.\stop_clipboard_service.ps1
```

This will terminate all running instances of the clipboard monitor.

## Usage

Once the service is running:

1. **Copy any image** containing medication information to your clipboard
   - Take a screenshot of a medication label
   - Copy an existing image file
   - Use the Print Screen key to capture an image

2. **Wait for the notification**
   - A toast notification will appear showing the detected medication and HPR number
   - The administration instructions will be automatically copied to your clipboard

3. **Paste the instructions** wherever needed
   - The administration instructions are now in your clipboard
   - Simply press Ctrl+V to paste them into any application

## Troubleshooting

If the service isn't working as expected:

1. Check if the service is running using `.\check_clipboard_service.ps1`
2. Review the log file at `clipboard_monitor.log` for error messages
3. Try stopping and restarting the service
4. Ensure the database contains the medication information you're looking for

## Logs

The service maintains a log file at `clipboard_monitor.log` that contains detailed information about its operation. This can be useful for troubleshooting issues.
