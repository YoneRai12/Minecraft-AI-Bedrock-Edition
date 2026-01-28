from dataclasses import dataclass
from typing import Optional, Tuple

@dataclass
class AgentState:
    position: Tuple[int, int, int] = (0, 0, 0)
    health: float = 20.0
    hunger: float = 20.0
    alive: bool = True
    active_task: str = "IDLE"

class StateManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(StateManager, cls).__new__(cls)
            cls._instance.state = AgentState()
        return cls._instance

    def update_position(self, pos: Tuple[int, int, int]):
        self.state.position = pos

    def update_health(self, health: float):
        self.state.health = health
        if self.state.health <= 0:
            self.state.alive = False

    def get_state(self) -> AgentState:
        return self.state

    def reset(self):
        self.state = AgentState()
