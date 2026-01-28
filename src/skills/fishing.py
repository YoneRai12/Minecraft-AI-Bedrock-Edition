import time
import cv2
import numpy as np
import math
from src.utils.input_controller import InputController

class FishingSkills:
    def __init__(self, controller: InputController):
        self.controller = controller
        self.state = "IDLE" # IDLE, CASTING, WAITING, REELING
        self.last_state_change = time.time()
        self.roi_size = 100 # Center 100x100
        self.prev_gray_roi = None
        self.motion_threshold = 5.0 # Sensitivity
        self.splash_cooldown = 2.0 # Wait 2s before accepting splash (to ignore cast splash)
        
    def update(self, frame: np.ndarray):
        """
        Main fishing loop.
        """
        current_time = time.time()
        
        if self.state == "IDLE":
             # Auto-start? Or wait for command?
             # For now, let's say we only fish if manually triggered into CASTING or by higher logic.
             pass

        elif self.state == "CASTING":
            print("[Fishing] Casting Rod")
            self.controller.gamepad.right_trigger_float(value_float=1.0) # Using API directly or via set_attack logic?
            # set_attack is duration based in primitive skills usually.
            # Here we just 'click'
            self.controller.set_attack(True)
            time.sleep(0.1) # Quick click
            self.controller.set_attack(False)
            
            self.state = "WAITING"
            self.last_state_change = current_time
            self.prev_gray_roi = None

        elif self.state == "WAITING":
            # 1. Timeout Check
            if current_time - self.last_state_change > 45.0:
                print("[Fishing] Timeout - Reeling in")
                self.state = "REELING"
                return

            # 2. Motion Detection (Splash)
            h, w, _ = frame.shape
            cx, cy = w // 2, h // 2
            half = self.roi_size // 2
            # ROI: Center of screen slightly down? deeply dependent on look angle.
            # Let's verify center for now.
            top, bottom = cy - half, cy + half
            left, right = cx - half, cx + half
            
            roi = frame[top:bottom, left:right]
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            # Blur to reduce noise
            gray = cv2.GaussianBlur(gray, (21, 21), 0)
            
            if self.prev_gray_roi is None:
                self.prev_gray_roi = gray
                return
                
            # Calc delta
            frame_delta = cv2.absdiff(self.prev_gray_roi, gray)
            thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
            motion_score = np.sum(thresh) / 255.0 # Number of changed pixels
            
            # Update prev
            self.prev_gray_roi = gray
            
            # Ignore initial splash from casting (first 2 seconds)
            if current_time - self.last_state_change < self.splash_cooldown:
                return

            # If motion > threshold -> SPLASH
            if motion_score > self.motion_threshold:
                print(f"[Fishing] Splash Detected! (Score: {motion_score})")
                self.state = "REELING"

        elif self.state == "REELING":
            print("[Fishing] Reeling in!")
            self.controller.set_attack(True)
            time.sleep(0.1)
            self.controller.set_attack(False)
            
            # Wait for reel anim
            time.sleep(0.5)
            self.state = "CASTING" # Loop forever?
            print("[Fishing] Recasting in 1s...")
            time.sleep(1.0)
            self.last_state_change = time.time()

    def start_fishing(self):
        self.state = "CASTING"

    def stop_fishing(self):
        self.state = "IDLE"
