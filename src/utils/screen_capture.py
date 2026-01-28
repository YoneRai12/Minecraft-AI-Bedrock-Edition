import cv2
import numpy as np
import dxcam
import time
import mss
import pygetwindow as gw
import threading
from typing import Optional, Tuple, Dict

class ScreenCapture:
    def __init__(self):
        """
        Initialize ScreenCapture with Multi-Monitor Support.
        """
        # 1. Get Monitor Layout using MSS (reliable source of truth for bounds)
        self.mss_ctx = mss.mss()
        self.monitors = self.mss_ctx.monitors # [0]=All, [1]=Primary, [2]=Secondary...
        
        self.current_monitor_idx = -1 # MSS Index (1-based)
        self.camera = None
        self.running = False
        
        self.target_window_title = "Minecraft" 
        
        # Default area
        self.region = (0, 0, 1920, 1080)
        self.monitor_width = 1920
        self.monitor_height = 1080
        
        # Stats
        self.capture_count = 0
        self.capture_rate = 0.0
        self.last_capture_time = time.time()
        
        # Thread defaults
        self.lock = threading.Lock()
        self.current_frame = None
        self.thread = None
        
        # Initial Window Search (will init camera)
        if not self.find_target_window():
             # Fallback to Primary (Index 1 for MSS, 0 for DXCam)
             print("[Screen] Window not found, defaulting to Primary Monitor.")
             self._init_camera(1)

    def _init_camera(self, mss_idx: int):
        """Initialize DXCam for a specific monitor (MSS Index 1..N)."""
        if self.current_monitor_idx == mss_idx and self.camera is not None:
            return
            
        print(f"[Screen] Switching Capture to Monitor {mss_idx}...")
        
        # Stop existing
        if self.camera is not None:
            if self.running:
                try: self.camera.stop() 
                except: pass
            del self.camera
            self.camera = None
            
        # Create new (DXCam uses 0-based index, MSS uses 1-based for specific monitors)
        dxcam_idx = mss_idx - 1
        try:
            self.camera = dxcam.create(device_idx=0, output_idx=dxcam_idx, output_color="BGR")
            self.current_monitor_idx = mss_idx
            
            # Update Dimensions
            self.monitor_width = self.camera.width
            self.monitor_height = self.camera.height
            
            # Restart capture if it was running
            if self.running:
                self.camera.start(target_fps=120, video_mode=True)
                
            print(f"[Screen] DXCam started on Output {dxcam_idx}")
        except Exception as e:
            print(f"[Screen] Init Error: {e}")
            # Fallback to 0 if failed
            if dxcam_idx != 0:
                print("[Screen] Retrying on Primary...")
                self._init_camera(1)

    def start(self):
        """Start the DXCam background capture."""
        if self.running: return
        self.running = True
        if self.camera:
            self.camera.start(target_fps=120, video_mode=True)
        print("[Screen] Capture started.")

    def stop(self):
        """Stop the DXCam capture."""
        self.running = False
        if self.camera and self.camera.is_capturing:
            self.camera.stop()
            
    def find_target_window(self):
        """Locate window, switch monitor if needed, update relative crop."""
        try:
            windows = gw.getWindowsWithTitle(self.target_window_title)
            if not windows:
                print(f"[Screen] ERROR: Window '{self.target_window_title}' NOT FOUND!")
                print("[Screen] Visible Windows:")
                all_wins = gw.getAllTitles()
                for t in all_wins:
                    if t.strip(): print(f" - {t}")
                return False

            if windows:
                win = windows[0]
                if win.isActive or not win.isMinimized:
                    # Window Global Coords
                    wx, wy, ww, wh = win.left, win.top, win.width, win.height
                    cx = wx + ww // 2
                    cy = wy + wh // 2
                    
                    # Find which monitor contains the center
                    target_idx = -1
                    for i, mon in enumerate(self.monitors):
                        if i == 0: continue # Skip 'All'
                        mx, my = mon["left"], mon["top"]
                        mw, mh = mon["width"], mon["height"]
                        
                        if (mx <= cx < mx + mw) and (my <= cy < my + mh):
                            target_idx = i
                            break
                    
                    if target_idx == -1:
                        target_idx = 1 # Default to primary if weird
                        
                    # Re-init camera if monitor changed
                    if target_idx != self.current_monitor_idx:
                        self._init_camera(target_idx)
                        
                    # Calculate Relative Coords for Crop
                    # DXCam captures the specific monitor's frame (0,0 is monitor top-left)
                    mon_info = self.monitors[target_idx]
                    
                    rel_left = max(0, int(wx - mon_info["left"]))
                    rel_top = max(0, int(wy - mon_info["top"]))
                    
                    # Clamp right/bottom to monitor size
                    mon_w, mon_h = mon_info["width"], mon_info["height"]
                    
                    rel_right = min(mon_w, rel_left + int(ww))
                    rel_bottom = min(mon_h, rel_top + int(wh))
                    
                    print(f"[Screen] Win: {wx},{wy} | Mon{target_idx}: {mon_info['left']},{mon_info['top']} | Crop: {rel_left},{rel_top} -> {rel_right},{rel_bottom}")
                    
                    if rel_right > rel_left and rel_bottom > rel_top:
                        self.region = (rel_left, rel_top, rel_right, rel_bottom)
                        return True
        except Exception as e:
            print(f"[Screen] Track Err: {e}")
        return False

    def capture_frame(self) -> Optional[np.ndarray]:
        """
        Returns the latest captured frame from DXCam.
        """
        if not self.running:
            return None
            
        # Get frame (Non-blocking usually in video_mode)
        frame = self.camera.get_latest_frame()
        
        if frame is None:
            return None
            
        # Crop to Window using Numpy Slicing
        left, top, right, bottom = self.region
        
        # Optimization: Only slice if not full screen (avoid copy if possible?)
        # Numpy slicing creates specific view, copy happens on resize anyway.
        if (left == 0 and top == 0 and right == self.monitor_width and bottom == self.monitor_height):
            img = frame
        else:
            img = frame[top:bottom, left:right]
            
        # Super-Fast Downscaling for High Res
        h, w = img.shape[:2]
        
        if w > 2500:
            # 4K -> ~1280 (Divide by 3) - Instant, no math
            img = img[::3, ::3]
        elif w > 1280:
            # 1440p/1080p -> Downscale (Divide by 2)
            img = img[::2, ::2]
        
        # CRITICAL: OpenCV requires C-contiguous arrays for drawing/processing
        # Slicing [::3] creates a view with strides, which causes "Layout incompatible" errors.
        img = np.ascontiguousarray(img)
        
        # Final sanity check resize if needed (rarely hit if slicing works)
        # Just to ensure we don't feed huge images to YOLO
        if img.shape[1] > 1280:
             scale = 1280 / img.shape[1]
             new_h = int(img.shape[0] * scale)
             img = cv2.resize(img, (1280, new_h), interpolation=cv2.INTER_NEAREST)
             
        # FPS Tracking
        self.capture_count += 1
        now = time.time()
        if now - self.last_capture_time >= 1.0:
            self.capture_rate = self.capture_count / (now - self.last_capture_time)
            self.capture_count = 0
            self.last_capture_time = now
            
        return img

    def close(self):
        """Release resources."""
        self.stop()
        # DXCam cleanup is handled by GC mostly, but stop() is important.

if __name__ == "__main__":
    # Test implementation
    cap = ScreenCapture()
    print("Starting DXCam test. Press 'q' to quit.")
    cap.start()
    
    last_time = time.time()
    frames = 0
    
    while True:
        frame = cap.capture_frame()
        if frame is None:
            continue
            
        # Display
        display_frame = cv2.resize(frame, (960, 540))
        cv2.imshow("DXCam Test", display_frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    cap.close()
    cv2.destroyAllWindows()
