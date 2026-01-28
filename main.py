import cv2
import time
import threading
import sys
import os

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

def main():
    print("Initializing MainkurafutoAI...")
    
    # Initialize Components
    try:
        cap = ScreenCapture()
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
    print("Press 'END' to QUIT bot.")
    print("Focus Minecraft window to see results (though this loop essentially just watches for now).")
    
    print("Focus Minecraft window to see results (though this loop essentially just watches for now).")
    
    last_time = time.time()
    was_retreating = False
    combat_mode = False
    fishing_mode = False
    
    try:
        while safety.active:
            # 1. Perception
            frame = cap.capture_frame()
            if frame is None:
                continue

            # 2. Safety Check
            if not safety.is_safe_to_operate():
                cv2.putText(frame, "PAUSED - F12 to Resume", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                cv2.imshow("Bot View", cv2.resize(frame, (960, 540)))
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                time.sleep(0.1)
                continue

            # 3. Perception & Mapping
            coords = coord_reader.process_frame(frame)
            if coords:
                state_mgr.update_position(coords)

            # --- REFLEX LAYER ---
            vision_result = vision_proc.process_frame(frame)
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

            # 4. Debug Display
            current_state = state_mgr.get_state()
            cv2.putText(frame, f"Pos: {current_state.position}", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            cv2.putText(frame, status_text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, status_color, 2)
            
            # Show small mask for debug
            if "mask" in vision_result:
                mask_display = cv2.resize(vision_result["mask"], (320, 180))
                # Overlay mask on bottom right
                h, w, _ = frame.shape
                frame[h-180:h, w-320:w] = cv2.cvtColor(mask_display, cv2.COLOR_GRAY2BGR)

            # Draw YOLO Detections
            detects = vision_result.get("detections", [])
            for det in detects:
                x1, y1, x2, y2 = det["box"]
                conf = det["conf"]
                label = det["label"]
                
                # Color based on label
                color = (0, 255, 255) # Yellow default
                if label == "person": color = (255, 0, 0) # Blue for person
                
                # Indicate target if Combat Mode
                if combat_mode and label == "person":
                    color = (0, 0, 255) # Red for target

                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame, f"{label} {conf:.2f}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

            # --- COMBAT LAYER ---
            if combat_mode and not was_retreating and not fishing_mode:
                h, w, _ = frame.shape
                combat_skills.update(detects, (w, h))
                cv2.putText(frame, "COMBAT MODE: ON", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            # --- FISHING LAYER ---
            if fishing_mode and not was_retreating:
                fishing_skills.update(frame)
                cv2.putText(frame, f"FISHING: {fishing_skills.state}", (50, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

            cv2.imshow("Bot View", cv2.resize(frame, (960, 540)))

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
                
    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        cap.close()
        cv2.destroyAllWindows()
        print("MainkurafutoAI Shutdown.")

if __name__ == "__main__":
    main()
