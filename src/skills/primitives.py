import time
from src.utils.input_controller import InputController

class PrimitiveSkills:
    def __init__(self, controller: InputController):
        self.controller = controller

    def move_forward(self, duration: float = 1.0):
        print(f"[Skill] Moving Forward for {duration}s")
        self.controller.move_forward(duration)

    def move_backward(self, duration: float = 1.0):
        print(f"[Skill] Moving Backward for {duration}s")
        self.controller.move_backward(duration)
        
    def jump(self):
        print("[Skill] Jumping")
        self.controller.jump()

    def attack(self, duration: float = 1.0):
        print(f"[Skill] Attacking for {duration}s")
        start = time.time()
        while time.time() - start < duration:
            self.controller.attack()
            time.sleep(0.1)

    def look_around(self):
        print("[Skill] Looking Around")
        # Simple scan
        self.controller.look_rotation(0.5, 0.0, 0.5)
        self.controller.look_rotation(-1.0, 0.0, 0.5)
        self.controller.look_rotation(0.5, 0.0, 0.5)

    def wait(self, duration: float = 1.0):
        print(f"[Skill] Waiting for {duration}s")
        time.sleep(duration)
