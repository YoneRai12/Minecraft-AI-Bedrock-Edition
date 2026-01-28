import keyboard
import time
import threading
from src.utils.input_controller import InputController

class SafetyMonitor:
    def __init__(self, controller: InputController):
        self.controller = controller
        self.active = True
        self.paused = False
        
    def start_monitoring(self):
        """Start the keyboard listener loop."""
        print("Safety Monitor Started. Press 'F12' to PAUSE/RESUME, 'END' to QUIT.")
        
        while self.active:
            if keyboard.is_pressed('F12'):
                self.paused = not self.paused
                state = "PAUSED" if self.paused else "RESUMED"
                print(f"*** EMERGENCY {state} ***")
                if self.paused:
                    self.controller.emergency_stop()
                time.sleep(0.5) # Debounce
                
            if keyboard.is_pressed('end'):
                print("*** KILL SWITCH ACTIVATED ***")
                self.controller.emergency_stop()
                self.active = False
                break
                
            time.sleep(0.01)

    def is_safe_to_operate(self) -> bool:
        return not self.paused

if __name__ == "__main__":
    # Test stub
    ctrl = InputController()
    monitor = SafetyMonitor(ctrl)
    monitor.start_monitoring()
