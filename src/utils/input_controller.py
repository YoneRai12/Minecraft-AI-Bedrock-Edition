try:
    import vgamepad as vg
    _VGAMEPAD_AVAILABLE = True
except ImportError:
    _VGAMEPAD_AVAILABLE = False
    print("Warning: 'vgamepad' not found. Virtual Controller disabled.")

import time
import threading

class InputController:
    def __init__(self):
        """
        Initialize Virtual Xbox 360 Controller (Non-blocking).
        """
        self.gamepad = None
        self._input_state = {
            "left_x": 0.0,
            "left_y": 0.0,
            "right_x": 0.0,
            "right_y": 0.0,
            "buttons": set(),
            "triggers": {"left": 0.0, "right": 0.0}
        }
        
        if _VGAMEPAD_AVAILABLE:
            try:
                self.gamepad = vg.VX360Gamepad()
                print("Virtual Controller Initialized.")
            except Exception as e:
                print(f"Failed to initialize Virtual Controller: {e}")

    def update(self):
        """Apply the current state to the virtual device."""
        if not self.gamepad: return

        try:
            # Apply Joystick States
            self.gamepad.left_joystick_float(
                x_value_float=self._input_state["left_x"], 
                y_value_float=self._input_state["left_y"]
            )
            self.gamepad.right_joystick_float(
                x_value_float=self._input_state["right_x"], 
                y_value_float=self._input_state["right_y"]
            )
            
            # Apply Trigger States
            self.gamepad.left_trigger_float(value_float=self._input_state["triggers"]["left"])
            self.gamepad.right_trigger_float(value_float=self._input_state["triggers"]["right"])
            
            # Apply Button States
            # Note: vgamepad buttons need to be pressed/released explicitly or reset every frame?
            # vgamepad is stateful. We should release all buttons not in the set, and press all in the set.
            # However, simpler approach: Reset allows clearing, but might be flicker-y.
            # Better: We just rely on the API. To properly handle buttons without clearing everything:
            # For this MVP, we only support a few buttons so let's just press them if active.
            # Creating a fresh report is complex with vgamepad properly.
            
            # Simplified approach: We assume transient button presses are handled by caller,
            # OR we just map specific buttons we care about.
            
            # Let's handle Jump (A) and Attack (RT - already triggers)
            if "JUMP" in self._input_state["buttons"]:
                self.gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
            else:
                self.gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)

            self.gamepad.update()
            
        except Exception as e:
            print(f"Error updating gamepad: {e}")

    def set_move(self, x: float, y: float):
        """Set movement vector (-1.0 to 1.0)."""
        self._input_state["left_x"] = float(x)
        self._input_state["left_y"] = float(y)
        self.update() # Immediate update for responsiveness

    def set_look(self, x: float, y: float):
        """Set look vector (-1.0 to 1.0)."""
        self._input_state["right_x"] = float(x)
        self._input_state["right_y"] = float(y)
        self.update()

    def set_jump(self, active: bool):
        if active:
            self._input_state["buttons"].add("JUMP")
        else:
            self._input_state["buttons"].discard("JUMP")
        self.update()

    def set_attack(self, active: bool):
        self._input_state["triggers"]["right"] = 1.0 if active else 0.0
        self.update()

    def emergency_stop(self):
        """Reset all inputs."""
        self._input_state = {
            "left_x": 0.0, "left_y": 0.0,
            "right_x": 0.0, "right_y": 0.0,
            "buttons": set(),
            "triggers": {"left": 0.0, "right": 0.0}
        }
        if self.gamepad:
            self.gamepad.reset()
            self.gamepad.update()

if __name__ == "__main__":
    controller = InputController()
    print("Testing non-blocking controller...")
    time.sleep(2)
    
    print("Moving Forward...")
    controller.set_move(0, 1.0)
    time.sleep(1)
    
    print("Stopping...")
    controller.set_move(0, 0)
    time.sleep(1)
