import sys
import os
import cv2
import time

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.screen_capture import ScreenCapture
from src.reflex.yolo_detector import YoloDetector

def check_vision():
    print("Initializing Vision Diagnostics...")
    
    cap = ScreenCapture()
    detector = YoloDetector()
    
    print("Capturing frame in 3 seconds... Switch to Minecraft!")
    time.sleep(3)
    
    frame = cap.capture_frame()
    if frame is None:
        print("Error: Could not capture frame.")
        return

    print("Running YOLO inference...")
    detections = detector.detect(frame)
    
    print(f"Found {len(detections)} objects:")
    for det in detections:
        print(f" - {det['label']} ({det['conf']:.2f}) at {det['box']}")
        
        # Draw
        x1, y1, x2, y2 = det["box"]
        label = f"{det['label']} {det['conf']:.2f}"
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
    output_path = "debug_vision.png"
    cv2.imwrite(output_path, frame)
    print(f"Annotated image saved to {os.path.abspath(output_path)}")
    
    # Show
    cv2.imshow("Debug Vision", cv2.resize(frame, (960, 540)))
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    check_vision()
