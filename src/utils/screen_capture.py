import cv2
import numpy as np
import mss
import time
from typing import Optional, Tuple, Dict

class ScreenCapture:
    def __init__(self, monitor_index: int = 1):
        """
        Initialize ScreenCapture.
        
        Args:
            monitor_index (int): Index of the monitor to capture (usually 1 is primary).
        """
        self.sct = mss.mss()
        self.monitor_index = monitor_index
        self.monitor = self.sct.monitors[self.monitor_index]
        self.target_window_title = "Minecraft" # Target window name (not strictly used by mss loop but good for config)
        
        # Default Full Screen Capture
        self.capture_area = {
            "top": self.monitor["top"],
            "left": self.monitor["left"],
            "width": self.monitor["width"],
            "height": self.monitor["height"]
        }

    def update_capture_area(self, region: Dict[str, int]):
        """
        Update the specific region to capture.
        
        Args:
           region (dict): Dictionary with keys 'top', 'left', 'width', 'height'.
        """
        self.capture_area = region

    def capture_frame(self) -> Optional[np.ndarray]:
        """
        Captures a single frame from the screen.
        
        Returns:
            np.ndarray: The captured image in BGR format (OpenCV default), or None if failed.
        """
        try:
            # Grab the data
            sct_img = self.sct.grab(self.capture_area)
            
            # Convert to numpy array
            img = np.array(sct_img)
            
            # Convert BGRA to BGR (remove alpha channel)
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            
            return img
        except Exception as e:
            print(f"Error capturing frame: {e}")
            return None

    def close(self):
        """Release resources."""
        self.sct.close()

if __name__ == "__main__":
    # Test implementation
    cap = ScreenCapture()
    print("Starting capture test. Press 'q' to quit.")
    
    last_time = time.time()
    frames = 0
    
    while True:
        frame = cap.capture_frame()
        if frame is None:
            continue
            
        # FPS Calculation
        frames += 1
        if time.time() - last_time > 1.0:
            print(f"FPS: {frames}")
            frames = 0
            last_time = time.time()
        
        # Display (Resize for visibility if 4k)
        display_frame = cv2.resize(frame, (960, 540))
        cv2.imshow("Screen Capture Test", display_frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    cap.close()
    cv2.destroyAllWindows()
