from typing import Callable, Dict, List, Any
from src.skills.primitives import PrimitiveSkills

class SkillRegistry:
    MIN_DURATION = 0.0
    MAX_DURATION = 5.0

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

    def _sanitize_args(self, cmd: str, raw_args: List[str]) -> List[float]:
        """Sanitize skill arguments and bound duration-like parameters."""
        if len(raw_args) > 1:
            raise ValueError("Too many arguments")

        if not raw_args:
            return []

        value = float(raw_args[0])
        bounded = min(max(value, self.MIN_DURATION), self.MAX_DURATION)

        if bounded != value:
            print(
                f"[Safety] Clamped {cmd} duration from {value} to {bounded} "
                f"(allowed {self.MIN_DURATION}-{self.MAX_DURATION}s)."
            )

        return [bounded]

    def execute_plan(self, plan: List[str]):
        """
        Execute a list of action strings.
        Format: "ACTION_NAME" or "ACTION_NAME arg1"
        """
        for step in plan:
            if not step or not step.strip():
                continue

            parts = step.split()
            if not parts:
                continue

            cmd = parts[0].upper()
            args = parts[1:]
            
            if cmd in self.skills:
                try:
                    parsed_args = self._sanitize_args(cmd, args)
                    self.skills[cmd](*parsed_args)
                except Exception as e:
                    print(f"Error executing skill '{step}': {e}")
            else:
                print(f"Unknown skill: {cmd}")
