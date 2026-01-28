import time
import math
from typing import List, Dict, Any, Tuple
from src.utils.input_controller import InputController

class CollectionSkills:
    def __init__(self, controller: InputController):
        self.controller = controller
        self.kp_steer = 0.003
        self.item_labels = ["backpack", "suitcase", "handbag", "tie", "bottle", "cup", "bowl", "orange", "apple"] 
        # YOLOv8n COCO labels that *might* misidentify as Minecraft items.
        # In reality, without custom training, this is a best-effort sketch.
        # We will also accept "person" if we want to follow players? No.
        # Ideally, we look for small objects.
        # For now, let's include "person" just so it does SOMETHING in testing until custom model.
        # self.item_labels.append("person") 

    def update(self, detections: List[Dict[str, Any]], screen_size: Tuple[int, int]):
        """
        Move towards the closest item.
        """
        target = self._find_closest_item(detections, screen_size)
        
        if target:
            # Steer
            self._move_to_target(target, screen_size)
        else:
            # Stop moving if no item
            # self.controller.set_move(0, 0) # Use with caution, might interrupt other layers
            pass

    def _find_closest_item(self, detections: List[Dict[str, Any]], screen_size: Tuple[int, int]) -> Dict[str, Any]:
        w, h = screen_size
        cx, cy = w / 2, h / 2
        
        best_target = None
        min_dist = float('inf')
        
        for det in detections:
            label = det.get("label", "")
            # If label matches our "Item" list (or if we have a custom model with 'dropped_item')
            # For testing with standard YOLO, we might struggle to find items.
            # Let's assume ANY small object that isn't a person is an item?
            # Or just use specific COCO classes like 'apple', 'bottle'.
            
            # TODO: Improve this with custom model
            if label not in self.item_labels:
                continue

            x1, y1, x2, y2 = det["box"]
            tx, ty = (x1 + x2) / 2, (y1 + y2) / 2
            
            # Prioritize distance to bottom-center (feet)
            dist = math.hypot(tx - cx, ty - h)
            
            if dist < min_dist:
                min_dist = dist
                best_target = det
        
        return best_target

    def _move_to_target(self, target: Dict[str, Any], screen_size: Tuple[int, int]):
        """
        Simple Visual Servoing: Steer towards target.
        """
        w, h = screen_size
        cx = w / 2
        
        x1, y1, x2, y2 = target["box"]
        tx = (x1 + x2) / 2
        
        # Steering (Left/Right)
        dx = tx - cx
        steer = dx * self.kp_steer
        steer = max(-1.0, min(1.0, steer))
        
        # Move Forward (Fixed speed)
        # Stop if very close (bottom of screen)
        # y2 is bottom of box. if y2 > h - margin, we are close.
        if y2 > h - 50:
            self.controller.set_move(0.0, 0.0) # Stop
            # Maybe look down?
        else:
            self.controller.set_move(0.0, 1.0) # Forward
            self.controller.set_look(steer, 0.0) # Steer
