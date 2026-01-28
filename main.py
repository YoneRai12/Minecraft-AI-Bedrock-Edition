import cv2
import time
import threading
import sys
import os
import numpy as np
import ctypes

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    ctypes.windll.user32.SetProcessDPIAware()

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.utils.screen_capture import ScreenCapture
from src.utils.input_controller import InputController
from src.reflex.safety_monitor import SafetyMonitor
from src.mapping.coordinate_reader import CoordinateReader
from src.core.state_manager import StateManager
from src.interface.command_center import CommandCenter
from src.reflex.vision_processor import VisionProcessor
from src.reflex.behaviors import ReflexBehaviors
from src.core.arbitrator import ActionArbitrator
from src.skills.combat import CombatSkills
from src.skills.fishing import FishingSkills

def resize_with_pad(image, target_width, target_height):
    """
    Resize image to fit within target dimensions while maintaining aspect ratio.
    Adds black borders (letterboxing) to center the image.
    """
    h, w = image.shape[:2]
    scale = min(target_width / w, target_height / h)
    nw, nh = int(w * scale), int(h * scale)
    
    image_resized = cv2.resize(image, (nw, nh))
    
    canvas = np.zeros((target_height, target_width, 3), dtype=np.uint8)
    x_off = (target_width - nw) // 2
    y_off = (target_height - nh) // 2
    
    canvas[y_off:y_off+nh, x_off:x_off+nw] = image_resized
    return canvas

def main():
    print("Initializing MainkurafutoAI...")
    
    # Initialize Components
    try:
        cap = ScreenCapture()
        cap.start() # Start background thread for FPS
        controller = InputController()
        safety = SafetyMonitor(controller)
        coord_reader = CoordinateReader()
        state_mgr = StateManager()
        cmd_center = CommandCenter(state_mgr, controller)
        vision_proc = VisionProcessor()
        reflex_action = ReflexBehaviors(controller)
        arbitrator = ActionArbitrator()
        combat_skills = CombatSkills(controller)
        fishing_skills = FishingSkills(controller)
    except Exception as e:
        print(f"Initialization Failed: {e}")
        return

    # Start Safety Monitor in background thread
    safety_thread = threading.Thread(target=safety.start_monitoring, daemon=True)
    safety_thread.start()

    # Start Command Center Input
    cmd_center.start_input_thread()

    print("AI Agent Initialized.")
    print("Press 'F12' to PAUSE bot.")
    print("Press 'C' to Toggle COMBAT MODE.")
    print("Press 'F' to Toggle FISHING MODE.")
    print("Press 'R' to Re-track Minecraft Window.")
    print("Press 'END' to QUIT bot.")
    print("Focus Minecraft window to see results (though this loop essentially just watches for now).")
    
    print("Focus Minecraft window to see results.")
    
    cv2.namedWindow("Bot View", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Bot View", 1280, 720) # Default convenient size

    last_time = time.time()
    was_retreating = False
    combat_mode = False
    fishing_mode = False
    
    try:
        while safety.active:
            # 1. Perception
            t0 = time.time()
            frame = cap.capture_frame()
            t1 = time.time()
            
            t1 = time.time()
            
            if frame is None:
                # Create a black placeholder to keep UI responsive
                blank = np.zeros((720, 1280, 3), np.uint8)
                cv2.putText(blank, "Waiting for video... (Check Console)", (400, 360), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                cv2.imshow("Bot View", blank)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                time.sleep(0.1)
                continue

            # 2. Safety Check
            if not safety.is_safe_to_operate():
                cv2.putText(frame, "PAUSED - F12 to Resume", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                cv2.imshow("Bot View", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                time.sleep(0.1)
                continue

            # 3. Perception & Mapping
            t2 = time.time()
            coords = coord_reader.process_frame(frame)
            t3 = time.time()
            if coords:
                state_mgr.update_position(coords)

            # --- REFLEX LAYER ---
            t4 = time.time()
            vision_result = vision_proc.process_frame(frame)
            t5 = time.time()
            
            lava_danger = vision_result.get("lava_detected", False)
            danger_level = vision_result.get("danger_level", 0.0)

            # Determine Reflex Proposal
            reflex_proposal = "RETREAT" if lava_danger else None
            
            # Arbitrate (Planning is None for now)
            action = arbitrator.determine_action(reflex_proposal, None, None)

            if action == "RETREAT":
                reflex_action.retreat_from_danger()
                was_retreating = True
                status_color = (0, 0, 255) # Red
                status_text = f"DANGER: LAVA ({danger_level:.1%})"
            else:
                if was_retreating:
                    reflex_action.stop_retreat() # Only stop if we were retreating
                    was_retreating = False
                status_color = (0, 255, 0) # Green
                status_text = "ACTIVE - SAFE"
            
            # Performance Debug
            # cap_ms = (t1 - t0) * 1000
            # coord_ms = (t3 - t2) * 1000
            # vis_ms = (t5 - t4) * 1000
            fps = 1.0 / (time.time() - last_time)
            last_time = time.time()
            
            # if fps < 30:
            #     print(f"[Lag] FPS:{fps:.1f} | Cap:{cap_ms:.1f}ms Coord:{coord_ms:.1f}ms Vis:{vis_ms:.1f}ms | Frame:{frame.shape}")

            # 4. Debug Display
            # Loop FPS (Green)
            cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
            
            # Real Capture FPS (Yellow)
            cap_fps = getattr(cap, 'capture_rate', 0.0)
            cv2.putText(frame, f"Cap: {cap_fps:.1f}", (200, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)

            # 2. Draw YOLO Detections (ALL)
            detects = vision_result.get("detections", [])
            for det in detects:
                label = det["label"]
                # Display everything as requested
                
                x1, y1, x2, y2 = det["box"]
                conf = det["conf"]
                
                # Color based on label
                color = (0, 255, 255) # Yellow default
                if label == "person": color = (255, 0, 0) # Blue for person
                
                # Indicate target if Combat Mode
                if combat_mode and label == "person":
                    color = (0, 0, 255) # Red for target

                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame, f"{label} {conf:.2f}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

            # 3. Device Info (Moved down to avoid overlap)
            device_name = vision_result.get("device", "Unknown")
            dev_color = (0, 255, 0) if "cpu" not in device_name.lower() else (0, 0, 255)
            cv2.putText(frame, f"Device: {device_name}", (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.7, dev_color, 2)

            # --- COMBAT LAYER ---
            if combat_mode and not was_retreating and not fishing_mode:
                h, w, _ = frame.shape
                combat_skills.update(detects, (w, h))
                cv2.putText(frame, "COMBAT MODE: ON", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            # --- FISHING LAYER ---
            if fishing_mode and not was_retreating:
                fishing_skills.update(frame)
                cv2.putText(frame, f"FISHING: {fishing_skills.state}", (50, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

            # Show resizable window (user controlled)
            # Handle Aspect Ratio
            try:
                rect = cv2.getWindowImageRect("Bot View")
                if rect and rect[2] > 0 and rect[3] > 0:
                    win_w, win_h = rect[2], rect[3]
                    display_frame = resize_with_pad(frame, win_w, win_h)
                    cv2.imshow("Bot View", display_frame)
                else:
                    cv2.imshow("Bot View", frame)
            except Exception:
                cv2.imshow("Bot View", frame) # Fallback

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('c'):
                combat_mode = not combat_mode
                fishing_mode = False # Mutual exclusive
                print(f"Combat Mode: {combat_mode}")
                if not combat_mode:
                    controller.set_look(0, 0)
                    controller.set_attack(False)
            elif key == ord('f'):
                fishing_mode = not fishing_mode
                combat_mode = False # Mutual exclusive
                if fishing_mode:
                    fishing_skills.start_fishing()
                else:
                    fishing_skills.stop_fishing()
                print(f"Fishing Mode: {fishing_mode}")
            elif key == ord('r'):
                print("Re-tracking window...")
                cap.find_target_window()
                
            # Resize Check (Optional)
            # if cv2.getWindowProperty("Bot View", cv2.WND_PROP_VISIBLE) < 1: break 
            
    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        cap.close()
        cv2.destroyAllWindows()
        print("MainkurafutoAI Shutdown.")

if __name__ == "__main__":
    main()
