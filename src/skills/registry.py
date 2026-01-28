from typing import Callable, Dict, List, Any
from src.skills.primitives import PrimitiveSkills

class SkillRegistry:
    def __init__(self, primitives: PrimitiveSkills):
        self.primitives = primitives
        self.skills: Dict[str, Callable] = {}
        self._register_defaults()

    def _register_defaults(self):
        self.register_skill("MOVE_FORWARD", self.primitives.move_forward)
        self.register_skill("MOVE_BACKWARD", self.primitives.move_backward)
        self.register_skill("JUMP", self.primitives.jump)
        self.register_skill("ATTACK", self.primitives.attack)
        self.register_skill("LOOK_AROUND", self.primitives.look_around)
        self.register_skill("WAIT", self.primitives.wait)

    def register_skill(self, name: str, func: Callable):
        self.skills[name.upper()] = func

    def execute_plan(self, plan: List[str]):
        """
        Execute a list of action strings.
        Format: "ACTION_NAME" or "ACTION_NAME arg1"
        """
        for step in plan:
            parts = step.split()
            cmd = parts[0].upper()
            args = parts[1:]
            
            if cmd in self.skills:
                try:
                    # Basic argument parsing (all floats for now)
                    parsed_args = [float(a) for a in args]
                    self.skills[cmd](*parsed_args)
                except Exception as e:
                    print(f"Error executing skill '{step}': {e}")
            else:
                print(f"Unknown skill: {cmd}")
