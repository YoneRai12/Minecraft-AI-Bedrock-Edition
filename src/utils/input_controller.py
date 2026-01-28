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
        Initialize Virtual Xbox 360 Controller.
        """
        self.gamepad = None
        if _VGAMEPAD_AVAILABLE:
            try:
                self.gamepad = vg.VX360Gamepad()
                print("Virtual Controller Initialized.")
            except Exception as e:
                print(f"Failed to initialize Virtual Controller: {e}")

    def press_button(self, button_code, duration: float = 0.1):
        """
        Press a button for a specific duration.
        """
        if not self.gamepad: return
        
        self.gamepad.press_button(button=button_code)
        self.gamepad.update()
        
        time.sleep(duration)
        
        self.gamepad.release_button(button=button_code)
        self.gamepad.update()

    def move_forward(self, duration: float = 0.5):
        """
        Move forward by pushing left stick up.
        """
        if not self.gamepad: return
        
        # Left Stick Y-axis up (Value between -32768 and 32767)
        # Up is positive in some libraries, but standard XInput Y is positive up.
        # vgamepad uses standard XInput.
        
        self.gamepad.left_joystick_float(x_value_float=0.0, y_value_float=1.0)
        self.gamepad.update()
        
        time.sleep(duration)
        
        self.gamepad.left_joystick_float(x_value_float=0.0, y_value_float=0.0)
        self.gamepad.update()

    def move_backward(self, duration: float = 0.5):
        if not self.gamepad: return
        self.gamepad.left_joystick_float(x_value_float=0.0, y_value_float=-1.0)
        self.gamepad.update()
        time.sleep(duration)
        self.gamepad.left_joystick_float(x_value_float=0.0, y_value_float=0.0)
        self.gamepad.update()

    def jump(self):
        """Press A button (Jump in default config)."""
        if not self.gamepad or not _VGAMEPAD_AVAILABLE: return
        self.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_A, duration=0.1)

    def attack(self):
        """Press Right Trigger (Attack/Mine)."""
        if not self.gamepad: return
        self.gamepad.right_trigger_float(value_float=1.0)
        self.gamepad.update()
        time.sleep(0.1)
        self.gamepad.right_trigger_float(value_float=0.0)
        self.gamepad.update()
    
    def look_rotation(self, x_float: float, y_float: float, duration: float = 0.1):
        """
        Move right stick.
        x_float, y_float: -1.0 to 1.0
        """
        if not self.gamepad: return
        self.gamepad.right_joystick_float(x_value_float=x_float, y_value_float=y_float)
        self.gamepad.update()
        time.sleep(duration)
        self.gamepad.right_joystick_float(x_value_float=0.0, y_value_float=0.0)
        self.gamepad.update()

    def emergency_stop(self):
        """Reset all inputs."""
        if not self.gamepad: return
        self.gamepad.reset()
        self.gamepad.update()

if __name__ == "__main__":
    controller = InputController()
    print("Testing controller in 3 seconds... Switch to Minecraft window!")
    time.sleep(3)
    
    print("Jumping...")
    controller.jump()
    time.sleep(1)
    
    print("Moving Forward...")
    controller.move_forward(1.0)
    
    print("Done.")
