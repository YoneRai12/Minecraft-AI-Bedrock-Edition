import cv2
import numpy as np
import pytesseract
import re
from typing import Tuple, Optional

class CoordinateReader:
    def __init__(self):
        """
        Initialize Coordinate Reader.
        Requires Tesseract-OCR installed on the system and in PATH, 
        or configured via pytesseract.pytesseract.tesseract_cmd.
        """
        self.last_position = (0, 0, 0)
        # Default region for Bedrock: Top left, but user might need to adjust
        # Approximate values for 1920x1080
        self.region = {"top": 0, "left": 0, "width": 400, "height": 100} 
        
    def set_region(self, top: int, left: int, width: int, height: int):
        self.region = {"top": top, "left": left, "width": width, "height": height}

    def process_frame(self, frame: np.ndarray) -> Optional[Tuple[int, int, int]]:
        """
        Extract coordinates from the frame.
        Expects format similar to "Position: 123, 64, 456"
        """
        if frame is None:
            return None

        # Crop to roi
        x, y, w, h = self.region["left"], self.region["top"], self.region["width"], self.region["height"]
        roi = frame[y:y+h, x:x+w]
        
        # Preprocessing for OCR
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        # Thresholding to isolate white text
        _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY) 
        
        # Invert if necessary (Tesseract likes black text on white usually, but works ok with white on black too)
        # Let's actually assume white text on game background.
        
        try:
            # psm 7 = Treat the image as a single text line.
            text = pytesseract.image_to_string(thresh, config='--psm 7')
            return self._parse_coordinates(text)
        except Exception as e:
            # Tesseract might not be found
            return None

    def _parse_coordinates(self, text: str) -> Optional[Tuple[int, int, int]]:
        """
        Parse text like "Position: 100, 60, 200"
        """
        # Regex to find three numbers separated by commas or spaces
        # Bedrock defaults: "Position: 1485, 71, 3"
        try:
            # Look for 3 integers (allowing minus signs)
            matches = re.findall(r'-?\d+', text)
            if len(matches) >= 3:
                # Take the first 3 numbers found
                x = int(matches[0])
                y = int(matches[1])
                z = int(matches[2])
                self.last_position = (x, y, z)
                return (x, y, z)
        except:
            pass
        return None

if __name__ == "__main__":
    # Test stub
    reader = CoordinateReader()
    print("CoordinateReader Initialized. (Requires Tesseract)")
