import time
from src.utils.input_controller import InputController

class ReflexBehaviors:
    def __init__(self, controller: InputController):
        self.controller = controller

    def retreat_from_danger(self):
        """
        Emergency routine: Stop active movement and move back.
        Called every frame when danger is active.
        """
        # Non-blocking backward input
        # -1.0 on Y axis is backward (standard XInput)
        self.controller.set_move(0.0, -1.0)
        
        # Optional: Trigger jump occasionally?
        # For simplicity, just move back.

    def stop_retreat(self):
        """Reset inputs after danger passes."""
        self.controller.set_move(0.0, 0.0)
