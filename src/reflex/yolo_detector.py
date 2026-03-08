import os
import hashlib
from dotenv import load_dotenv
import cv2
import numpy as np
from ultralytics import YOLO
from typing import List, Dict, Any

load_dotenv()

class YoloDetector:
    def __init__(self, model_path: str = "yolo11x.pt"):
        self.device = os.getenv("YOLO_DEVICE", None) # None = Auto (GPU if avail)
        print(f"[YOLO] Loading model: {model_path} (Device: {self.device if self.device else 'Auto'})...")

        if not self._is_model_trusted(model_path):
            self.model = None
            return

        try:
            self.model = YOLO(model_path)
            # Warmup
            print("[YOLO] Model loaded. Warming up...")
            # self.model.predict(np.zeros((640, 640, 3), dtype=np.uint8), verbose=False, device=self.device) 
        except Exception as e:
            print(f"[YOLO] Error loading model: {e}")
            self.model = None

    def _is_model_trusted(self, model_path: str) -> bool:
        if not model_path.lower().endswith('.pt'):
            return True

        expected_sha256 = os.getenv("YOLO_MODEL_SHA256", "").strip().lower()
        if expected_sha256:
            try:
                with open(model_path, "rb") as f:
                    actual_sha256 = hashlib.sha256(f.read()).hexdigest()
            except OSError as e:
                print(f"[YOLO] Could not read model for hash validation: {e}")
                return False

            if actual_sha256 != expected_sha256:
                print("[YOLO] Refusing to load .pt model: SHA256 hash mismatch.")
                return False
            return True

        if os.getenv("ALLOW_UNSAFE_YOLO_PT", "").strip() == "1":
            print("[YOLO] Warning: loading .pt model without hash validation.")
            return True

        print(
            "[YOLO] Refusing to load .pt model without trust settings. "
            "Set YOLO_MODEL_SHA256 to the expected hash or ALLOW_UNSAFE_YOLO_PT=1."
        )
        return False

    def detect(self, frame: np.ndarray, conf_threshold: float = 0.5) -> List[Dict[str, Any]]:
        """
        Run inference on the frame.
        Returns a list of detections: [{"box": [x1,y1,x2,y2], "conf": 0.9, "cls": "person", "label": "Steve"}]
        """
        if self.model is None:
            return []

        try:
            results = self.model.predict(frame, conf=conf_threshold, verbose=False, device=self.device)
        except RuntimeError as e:
            if "CUDA" in str(e) and self.device != 'cpu':
                print(f"[YOLO] CUDA Error detected ({e}). Falling back to CPU for stability.")
                self.device = 'cpu'
                results = self.model.predict(frame, conf=conf_threshold, verbose=False, device='cpu')
            else:
                print(f"[YOLO] Critical Inference Error: {e}")
                return []
        except Exception as e:
            print(f"[YOLO] Unexpected Error: {e}")
            return []

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
