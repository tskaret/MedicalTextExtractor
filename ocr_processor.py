import os
import cv2
import numpy as np
import pytesseract
from PIL import Image
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('ocr_processor.log')
    ]
)

# Import the tesseract path configuration
try:
    from tesseract_path import *
except ImportError:
    pass

class OCRProcessor:
    def __init__(self, tesseract_cmd=None, language='nor'):
        """
        Initialize the OCR processor.
        
        Args:
            tesseract_cmd (str, optional): Path to the Tesseract executable.
            language (str, optional): Language for OCR. Default is Norwegian ('nor').
        """
        self.logger = logging.getLogger("OCRProcessor")
        
        # Set path to tesseract executable if provided
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        else:
            # Try to find tesseract in common locations
            common_locations = [
                r'C:\Program Files\Tesseract-OCR\tesseract.exe',
                r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'
            ]
            for location in common_locations:
                if os.path.exists(location):
                    pytesseract.pytesseract.tesseract_cmd = location
                    break
        
        # Log the tesseract path being used
        self.logger.info(f"Using Tesseract path: {pytesseract.pytesseract.tesseract_cmd}")
        
        self.language = language
    
    def preprocess_image(self, image):
        """
        Preprocess the image to improve OCR results.
        
        Args:
            image: Image as numpy array or PIL Image
            
        Returns:
            Preprocessed image as numpy array
        """
        # Convert PIL Image to numpy array if necessary
        if isinstance(image, Image.Image):
            image = np.array(image)
        
        # Convert to grayscale if the image is in color
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Noise removal
        kernel = np.ones((1, 1), np.uint8)
        opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
        
        return opening
    
    def extract_text(self, image, preprocess=True):
        """
        Extract text from an image.
        
        Args:
            image: Image as file path, numpy array, or PIL Image
            preprocess (bool): Whether to preprocess the image
            
        Returns:
            Extracted text as string
        """
        try:
            # Handle different input types
            if isinstance(image, str):
                # Image is a file path
                if not os.path.exists(image):
                    self.logger.error(f"Image file not found: {image}")
                    return ""
                image = cv2.imread(image)
            elif isinstance(image, np.ndarray):
                # Image is already a numpy array
                pass
            elif isinstance(image, Image.Image):
                # Image is a PIL Image
                image = np.array(image)
            else:
                self.logger.error(f"Unsupported image type: {type(image)}")
                return ""
            
            # Preprocess the image if requested
            if preprocess:
                image = self.preprocess_image(image)
            
            # Extract text using pytesseract
            text = pytesseract.image_to_string(image, lang=self.language)
            
            return text
        except Exception as e:
            self.logger.error(f"Error extracting text: {str(e)}")
            return ""
    
    def extract_text_with_position(self, image, preprocess=True):
        """
        Extract text from an image with position information.
        
        Args:
            image: Image as file path, numpy array, or PIL Image
            preprocess (bool): Whether to preprocess the image
            
        Returns:
            List of dictionaries with text and position information
        """
        try:
            # Handle different input types
            if isinstance(image, str):
                # Image is a file path
                if not os.path.exists(image):
                    self.logger.error(f"Image file not found: {image}")
                    return []
                image = cv2.imread(image)
            elif isinstance(image, np.ndarray):
                # Image is already a numpy array
                pass
            elif isinstance(image, Image.Image):
                # Image is a PIL Image
                image = np.array(image)
            else:
                self.logger.error(f"Unsupported image type: {type(image)}")
                return []
            
            # Preprocess the image if requested
            if preprocess:
                processed_image = self.preprocess_image(image)
            else:
                processed_image = image
            
            # Extract text with bounding box information
            data = pytesseract.image_to_data(
                processed_image, lang=self.language, output_type=pytesseract.Output.DICT
            )
            
            # Combine the data into a list of dictionaries
            result = []
            for i in range(len(data['text'])):
                if data['text'][i].strip():  # Only include non-empty text
                    result.append({
                        'text': data['text'][i],
                        'left': data['left'][i],
                        'top': data['top'][i],
                        'width': data['width'][i],
                        'height': data['height'][i],
                        'conf': data['conf'][i]
                    })
            
            return result
        except Exception as e:
            self.logger.error(f"Error extracting text with position: {str(e)}")
            return []


# Example usage
if __name__ == "__main__":
    # Initialize OCR processor
    ocr = OCRProcessor()
    
    # Example: Extract text from an image file
    image_path = "sample_image.jpg"
    if os.path.exists(image_path):
        print("Extracting text from image...")
        text = ocr.extract_text(image_path)
        print("Extracted text:")
        print(text)
    else:
        print(f"Sample image {image_path} not found. Please provide an image to test.")
