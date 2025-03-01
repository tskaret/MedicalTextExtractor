@echo off
echo Starting clipboard monitor with med_text_env conda environment...
call conda activate d:\Conda.env\med_text_env
if %ERRORLEVEL% NEQ 0 (
    echo Failed to activate environment. Please run install_packages.bat first.
    exit /b 1
)
echo Environment activated successfully.
echo Running clipboard_monitor.py...
python "%~dp0clipboard_monitor.py"
