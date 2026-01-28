import cv2
import numpy as np
from typing import Dict, Any, Tuple, List
from src.reflex.yolo_detector import YoloDetector

class VisionProcessor:
    def __init__(self):
        # Define Lava Color Range (HSV)
        # Lava is generally bright orange/red -> yellow
        # Note: OpenCV HSV ranges are H: 0-179, S: 0-255, V: 0-255
        
        # Lower bound for orange/red
        # Lower bound (Tightened to exclude red blocks, focus on glowing orange)
        self.lava_lower = np.array([5, 180, 180]) 
        # Upper bound 
        self.lava_upper = np.array([35, 255, 255])
        
        # Area threshold to trigger warning (percentage of ROI)
        self.danger_threshold = 0.05 

        # YOLO Detector
        self.yolo = YoloDetector() # Will load detection model
        self.frame_count = 0
        # RTX 5090 can handle every frame. No skipping needed for 60FPS.
        self.skip_frames = 1 
        self.last_detections = [] 
        
        # Filter for Minecraft relevance (COCO classes)
        # 0: person (Player/Villager)
        # 15: cat, 16: dog, 17: horse, 18: sheep, 19: cow, 20: elephant, 21: bear, 22: zebra, 23: giraffe
        self.allowed_classes = {0, 15, 16, 17, 18, 19, 20, 21, 22, 23} 

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
        
        # 2. Object Detection (YOLO)
        self.frame_count += 1
        if self.frame_count % self.skip_frames == 0:
            # Lower confidence to catch stationary/partial objects
            raw_detections = self.yolo.detect(frame, conf_threshold=0.15)
            # Filter garbage (chairs, dining tables, etc.)
            self.last_detections = [
                d for d in raw_detections 
                if d['cls_id'] in self.allowed_classes
            ]
            
        return {
            "lava_detected": lava_detected,
            "danger_level": coverage,
            "mask": mask, # For debug visualization
            "detections": self.last_detections,
            "device": str(self.yolo.model.device) if (self.yolo and self.yolo.model) else "N/A"
        }

if __name__ == "__main__":
    # Test stub
    vp = VisionProcessor()
    print("VisionProcessor Initialized.")
