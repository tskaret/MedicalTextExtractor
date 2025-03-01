@echo off
echo Activating med_text_env conda environment...
call conda activate d:\Conda.env\med_text_env
if %ERRORLEVEL% NEQ 0 (
    echo Failed to activate environment. Please run setup_conda_env.ps1 first.
    exit /b 1
)
echo Environment activated successfully.
echo.
echo You can now run the following commands:
echo - python process_clipboard_image.py
echo - python clipboard_monitor.py
echo - .\start_clipboard_service.ps1
echo.
cmd /k
