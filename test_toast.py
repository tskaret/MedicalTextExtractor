#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script for toast notifications
"""

from win10toast import ToastNotifier
import time

print("Testing toast notifications...")

# Create a toast notifier
toaster = ToastNotifier()

# Show a test notification
print("Showing toast notification...")
toaster.show_toast(
    "Test Notification",
    "This is a test notification from Medical Text Extractor",
    duration=10,
    threaded=False  # Use non-threaded for testing
)

print("Toast notification should have appeared.")
print("If you didn't see it, there might be an issue with the win10toast package.")
