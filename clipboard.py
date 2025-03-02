import time
import pyperclip
from PIL import ImageGrab, Image, ImageDraw
from datetime import datetime
import win32api
import win32con  # Add this import
import threading
import pystray

def is_image_in_clipboard():
    try:
        img = ImageGrab.grabclipboard()
        if isinstance(img, Image.Image):
            return True
    except Exception as e:
        print(f"Error checking clipboard image: {e}")
    return False

def show_dialog(message):
    win32api.MessageBox(0, message, "Clipboard Monitor", win32con.MB_OK)

def clipboard_monitor():
    while True:
        if is_image_in_clipboard():
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            pyperclip.copy(f"Image {timestamp}")
            print(f"Image detected. Clipboard updated with timestamp: {timestamp}")
            show_dialog(f"Image detected in clipboard at {timestamp}")
        time.sleep(3)

def create_image():
    # Create a blank image with a white background
    image = Image.new("RGB", (64, 64), "white")
