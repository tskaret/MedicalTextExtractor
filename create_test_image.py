#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Create a test image with medication information
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_test_image(filename="test_medication.png"):
    """Create a test image with medication information."""
    # Create a white image
    width, height = 800, 600
    image = Image.new('RGB', (width, height), color='white')
    
    # Get a drawing context
    draw = ImageDraw.Draw(image)
    
    # Try to use a font
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except IOError:
        font = ImageFont.load_default()
    
    # Add text to the image
    text = """
    HPR: 10017852
    
    Fosamax
    
    Dosering: 1 tablett ukentlig
    """
    
    # Draw the text
    draw.text((50, 50), text, fill='black', font=font)
    
    # Save the image
    image.save(filename)
    print(f"Test image created: {filename}")
    
    return os.path.abspath(filename)

if __name__ == "__main__":
    image_path = create_test_image()
    print(f"Image saved to: {image_path}")
