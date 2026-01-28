import time
from src.utils.input_controller import InputController

class PrimitiveSkills:
    def __init__(self, controller: InputController):
        self.controller = controller

    def move_forward(self, duration: float = 1.0):
        print(f"[Skill] Moving Forward for {duration}s")
        self.controller.set_move(0.0, 1.0)
        time.sleep(duration)
        self.controller.set_move(0.0, 0.0)

    def move_backward(self, duration: float = 1.0):
        print(f"[Skill] Moving Backward for {duration}s")
        self.controller.set_move(0.0, -1.0)
        time.sleep(duration)
        self.controller.set_move(0.0, 0.0)
        
    def jump(self):
        print("[Skill] Jumping")
        self.controller.set_jump(True)
        time.sleep(0.1)
        self.controller.set_jump(False)

    def attack(self, duration: float = 1.0):
        print(f"[Skill] Attacking for {duration}s")
        self.controller.set_attack(True)
        time.sleep(duration)
        self.controller.set_attack(False)

    def look_around(self):
        print("[Skill] Looking Around")
        # Scan: Right -> Left -> Center
        self.controller.set_look(0.5, 0.0)
        time.sleep(0.5)
        self.controller.set_look(-1.0, 0.0)
        time.sleep(0.5)
        self.controller.set_look(0.5, 0.0)
        time.sleep(0.5)
        self.controller.set_look(0.0, 0.0)

    def wait(self, duration: float = 1.0):
        print(f"[Skill] Waiting for {duration}s")
        time.sleep(duration)
