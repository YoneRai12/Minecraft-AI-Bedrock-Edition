import time
import math
from typing import List, Dict, Any, Tuple
from src.utils.input_controller import InputController

class CombatSkills:
    def __init__(self, controller: InputController):
        self.controller = controller
        # PID Constants for Aiming
        self.kp_x = 0.002 # Sensitivity X
        self.kp_y = 0.002 # Sensitivity Y
        self.attack_range_pixels = 50 # If within this center distance, attack

    def update(self, detections: List[Dict[str, Any]], screen_size: Tuple[int, int]):
        """
        Main loop for combat. Finds best target and executes aim/attack.
        Should be called every frame if Combat Mode is active.
        """
        target = self._find_best_target(detections, screen_size)
        
        if target:
            # Aim
            self._aim_at_target(target, screen_size)
            
            # Attack if aimed
            if self._is_aimed_at(target, screen_size):
                self.controller.set_attack(True)
            else:
                self.controller.set_attack(False) # Stop attacking if lost aim? Or keep spamming?
                # Usually spamming is fine in Bedrock PVE
        else:
            # No target, relax inputs
            self.controller.set_look(0.0, 0.0)
            self.controller.set_attack(False)

    def _find_best_target(self, detections: List[Dict[str, Any]], screen_size: Tuple[int, int]) -> Dict[str, Any]:
        """
        Select the most threatening or closest target.
        For now: Select the target closest to the crosshair.
        """
        if not detections:
            return None
            
        w, h = screen_size
        cx, cy = w / 2, h / 2
        
        best_target = None
        min_dist = float('inf')
        
        for det in detections:
            # Filter by label (Assuming 'person' is the enemy for test, normally 'zombie', 'skeleton' etc)
            label = det.get("label", "")
            if label != "person": 
                continue
                
            x1, y1, x2, y2 = det["box"]
            tx, ty = (x1 + x2) / 2, (y1 + y2) / 2
            
            # Distance to crosshair
            dist = math.hypot(tx - cx, ty - cy)
            
            if dist < min_dist:
                min_dist = dist
                best_target = det
        
        return best_target

    def _aim_at_target(self, target: Dict[str, Any], screen_size: Tuple[int, int]):
        """
        Calculate stick inputs to move crosshair to target center.
        """
        w, h = screen_size
        cx, cy = w / 2, h / 2
        
        x1, y1, x2, y2 = target["box"]
        tx, ty = (x1 + x2) / 2, (y1 + y2) / 2
        
        dx = tx - cx
        dy = ty - cy
        
        # Simple P-Control
        # Output should be -1.0 to 1.0
        look_x = dx * self.kp_x
        look_y = dy * self.kp_y # Inverted? XInput RightStick Y Up is usually positive, but screen Y down is positive.
        # Screen Y increases downwards.
        # Stick Y: Up (negative look up? or positive?)
        # Typically: Stick Y+ -> Look Up (View trace goes up, pixels move down)
        # Wait, if I want to look at a pixel BELOW current center (dy > 0), I need to pitch DOWN.
        # Pitch Down usually corresponds to Stick Y- (or Y+ depending on config).
        # Let's assume standard: Y- is Down, Y+ is Up.
        # If target is below (dy > 0), we want Y- (Down). So inverse.
        
        out_x = max(-1.0, min(1.0, look_x))
        out_y = max(-1.0, min(1.0, -look_y)) 
        
        self.controller.set_look(out_x, out_y)

    def _is_aimed_at(self, target: Dict[str, Any], screen_size: Tuple[int, int]) -> bool:
        """Check if crosshair is within target box."""
        w, h = screen_size
        cx, cy = w / 2, h / 2
        
        x1, y1, x2, y2 = target["box"]
        
        # Check center with some margin
        margin = 0 # strict
        return (x1 - margin <= cx <= x2 + margin) and (y1 - margin <= cy <= y2 + margin)
