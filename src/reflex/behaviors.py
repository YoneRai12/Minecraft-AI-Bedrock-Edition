import time
from src.utils.input_controller import InputController

class ReflexBehaviors:
    def __init__(self, controller: InputController):
        self.controller = controller

    def retreat_from_danger(self):
        """
        Emergency routine: Stop active movement, look down (?) or just move back.
        For now: Simple Backward + Jump to clear obstacles.
        """
        # print("!!! REFLEX: RETREATING !!!")
        
        # 1. Stop processing other inputs (handled by arbitrator effectively by overriding)
        
        # 2. Move Backward
        # We can't block the main thread for too long, but reflex needs to be immediate.
        # Since this is called every frame while danger exists, we just execute a short burst of input.
        
        self.controller.press_button(self.controller.gamepad.XUSB_GAMEPAD_S if self.controller.gamepad else 0, duration=0.0) 
        # Note: input_controller.move_backward sleeps. We might need a non-blocking version for real-time loops.
        # But efficiently, we can just trigger "hold back" state.
        
        # For this prototype, we'll use the existing method but with very short duration to avoid blocking loop too much
        # Ideally, we should set a "state" of the controller, not sleep.
        
        # TODO: Refactor InputController to be state-based (SetStick(x,y)) rather than Action-based (Move(1s)).
        # For now, let's just do a quick backward pulse.
        # However, the current move_backward sleeps. Let's use raw gamepad access if available or add a method.
        
        if self.controller.gamepad:
            # Non-blocking backward input
            self.controller.gamepad.left_joystick_float(x_value_float=0.0, y_value_float=-1.0)
            self.controller.gamepad.update()
        
        # Optional: Place block down? (Too complex for simple reflex right now)

    def stop_retreat(self):
        """Reset inputs after danger passes."""
        if self.controller.gamepad:
            self.controller.gamepad.left_joystick_float(x_value_float=0.0, y_value_float=0.0)
            self.controller.gamepad.update()
