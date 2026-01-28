import cv2
import numpy as np
from typing import Dict, Any, Tuple

class VisionProcessor:
    def __init__(self):
        # Define Lava Color Range (HSV)
        # Lava is generally bright orange/red -> yellow
        # Note: OpenCV HSV ranges are H: 0-179, S: 0-255, V: 0-255
        
        # Lower bound for orange/red
        self.lava_lower = np.array([0, 150, 150]) 
        # Upper bound for orange/yellow
        self.lava_upper = np.array([30, 255, 255])
        
        # Area threshold to trigger warning (percentage of ROI)
        self.danger_threshold = 0.05 

    def process_frame(self, frame: np.ndarray) -> Dict[str, Any]:
        """
        Analyze the frame for hazards.
        Returns a dictionary with hazard info.
        """
        if frame is None:
            return {"lava_detected": False, "danger_level": 0.0}

        height, width, _ = frame.shape
        
        # 1. Underside / Footer ROI (Detecting lava at feet)
        # Check bottom 40% of the screen
        roi_h = int(height * 0.4)
        roi_top = height - roi_h
        roi = frame[roi_top:height, 0:width]
        
        # Convert to HSV
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        
        # Threshold
        mask = cv2.inRange(hsv, self.lava_lower, self.lava_upper)
        
        # Calculate coverage
        pixel_count = cv2.countNonZero(mask)
        total_pixels = roi_h * width
        coverage = pixel_count / total_pixels
        
        lava_detected = coverage > self.danger_threshold
        
        return {
            "lava_detected": lava_detected,
            "danger_level": coverage,
            "mask": mask # For debug visualization
        }

if __name__ == "__main__":
    # Test stub
    vp = VisionProcessor()
    print("VisionProcessor Initialized.")
