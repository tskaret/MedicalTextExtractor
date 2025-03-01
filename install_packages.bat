@echo off
echo Installing required packages in the med_text_env conda environment...
call conda activate d:\Conda.env\med_text_env
pip install opencv-python pillow pyautogui pynput pyperclip pytesseract win10toast
echo Package installation completed.
pip list
