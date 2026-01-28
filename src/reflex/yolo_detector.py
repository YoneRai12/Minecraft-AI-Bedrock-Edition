import cv2
import numpy as np
from ultralytics import YOLO
from typing import List, Dict, Any

class YoloDetector:
    def __init__(self, model_path: str = "yolov8n.pt"):
        print(f"[YOLO] Loading model: {model_path}...")
        try:
            self.model = YOLO(model_path)
            # Warmup
            print("[YOLO] Model loaded. Warming up...")
            # self.model.predict(np.zeros((640, 640, 3), dtype=np.uint8), verbose=False) # Optional warmup
        except Exception as e:
            print(f"[YOLO] Error loading model: {e}")
            self.model = None

    def detect(self, frame: np.ndarray, conf_threshold: float = 0.5) -> List[Dict[str, Any]]:
        """
        Run inference on the frame.
        Returns a list of detections: [{"box": [x1,y1,x2,y2], "conf": 0.9, "cls": "person", "label": "Steve"}]
        """
        if self.model is None:
            return []

        results = self.model.predict(frame, conf=conf_threshold, verbose=False, device='cpu')
        detections = []
        
        for r in results:
            boxes = r.boxes
            for box in boxes:
                # Bounding Box
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                
                # Confidence
                conf = float(box.conf[0])
                
                # Class Name
                cls_id = int(box.cls[0])
                label = self.model.names[cls_id]
                
                detections.append({
                    "box": [int(x1), int(y1), int(x2), int(y2)],
                    "conf": conf,
                    "cls_id": cls_id,
                    "label": label
                })
        
        return detections
