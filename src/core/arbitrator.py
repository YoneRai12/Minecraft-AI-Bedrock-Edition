from typing import Optional, Dict

class ActionArbitrator:
    def __init__(self):
        self.current_priority = 0 # 0: Idle, 10: Plan, 50: User, 100: Reflex
        self.active_layer = "IDLE"

    def determine_action(self, reflex_proposal: Optional[str], plan_proposal: Optional[str], user_input: Optional[str]) -> str:
        """
        Decide which action to execute based on priority.
        Returns the action string.
        """
        # 1. Reflex has highest priority (Safety)
        if reflex_proposal:
            self.current_priority = 100
            self.active_layer = "REFLEX"
            return reflex_proposal

        # 2. User Input (Manual override or Command)
        # Assuming manual input is handled by hardware directly usually, 
        # but if we had a software override system:
        if user_input:
             self.current_priority = 50
             self.active_layer = "USER"
             return user_input

        # 3. Planning (AI Goal)
        if plan_proposal:
            self.current_priority = 10
            self.active_layer = "PLAN"
            return plan_proposal

        self.current_priority = 0
        self.active_layer = "IDLE"
        return "IDLE"
