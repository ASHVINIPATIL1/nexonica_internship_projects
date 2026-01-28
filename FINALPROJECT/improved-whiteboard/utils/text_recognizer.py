"""
Text Recognition Module
Converts hand-written text on canvas to digital text using OCR
"""

import cv2
import numpy as np
from PIL import Image
import pytesseract

class TextRecognizer:
    def __init__(self):
        """Initialize text recognizer"""
        # Configure Tesseract path (uncomment for Windows)
        # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        pass
    
    def recognize_from_canvas(self, canvas):
        """
        Recognize text from canvas drawing
        
        Args:
            canvas: numpy array (BGR image) - the PURE canvas, not video overlay
            
        Returns:
            str: Recognized text
        """
        # Step 1: Convert canvas to grayscale
        gray = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
        
        # Step 2: Invert (make text black on white background)
        # Currently: colored text on black background
        # OCR needs: black text on white background
        inverted = cv2.bitwise_not(gray)
        
        # Step 3: Apply threshold to make it pure black and white
        _, binary = cv2.threshold(inverted, 50, 255, cv2.THRESH_BINARY)
        
        # Step 4: Optional - Clean up noise
        # Use morphological operations to remove small noise
        kernel = np.ones((2, 2), np.uint8)
        cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        
        # Step 5: Resize for better OCR (Tesseract works better with larger text)
        # Scale up 2x
        height, width = cleaned.shape
        resized = cv2.resize(cleaned, (width * 2, height * 2), interpolation=cv2.INTER_CUBIC)
        
        # Step 6: Save preprocessed image (for debugging)
        cv2.imwrite('preprocessed_for_ocr.png', resized)
        print("💾 Saved preprocessed image: preprocessed_for_ocr.png")
        
        # Step 7: Convert to PIL Image
        pil_image = Image.fromarray(resized)
        
        # Step 8: Run Tesseract OCR
        # Configure Tesseract for better handwriting recognition
        custom_config = r'--oem 3 --psm 7'  # PSM 7 = single line of text
        text = pytesseract.image_to_string(pil_image, config=custom_config)
        
        return text.strip()
    
    def recognize_with_confidence(self, canvas):
        """
        Recognize text with confidence scores
        
        Returns:
            dict: {'text': str, 'confidence': float, 'details': list}
        """
        # Preprocess
        gray = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
        inverted = cv2.bitwise_not(gray)
        _, binary = cv2.threshold(inverted, 50, 255, cv2.THRESH_BINARY)
        kernel = np.ones((2, 2), np.uint8)
        cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        height, width = cleaned.shape
        resized = cv2.resize(cleaned, (width * 2, height * 2), interpolation=cv2.INTER_CUBIC)
        pil_image = Image.fromarray(resized)
        
        # Get detailed results with confidence
        data = pytesseract.image_to_data(pil_image, output_type=pytesseract.Output.DICT)
        
        # Extract text with confidence > 60%
        text_parts = []
        confidences = []
        
        for i in range(len(data['text'])):
            if int(data['conf'][i]) > 60:  # Only high-confidence text
                text_parts.append(data['text'][i])
                confidences.append(data['conf'][i])
        
        full_text = ' '.join(text_parts)
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        return {
            'text': full_text.strip(),
            'confidence': avg_confidence,
            'details': data
        }
    
    def preprocess_and_show(self, canvas):
        """
        Show preprocessing steps for debugging
        Useful to see what Tesseract actually sees
        """
        # Original
        cv2.imshow('1. Original Canvas', canvas)
        
        # Grayscale
        gray = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
        cv2.imshow('2. Grayscale', gray)
        
        # Inverted
        inverted = cv2.bitwise_not(gray)
        cv2.imshow('3. Inverted', inverted)
        
        # Binary
        _, binary = cv2.threshold(inverted, 50, 255, cv2.THRESH_BINARY)
        cv2.imshow('4. Binary (Black & White)', binary)
        
        # Cleaned
        kernel = np.ones((2, 2), np.uint8)
        cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        cv2.imshow('5. Cleaned', cleaned)
        
        # Resized
        height, width = cleaned.shape
        resized = cv2.resize(cleaned, (width * 2, height * 2), interpolation=cv2.INTER_CUBIC)
        cv2.imshow('6. Final (What OCR Sees)', resized)
        
        cv2.waitKey(0)
        cv2.destroyAllWindows()
