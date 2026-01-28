from typing import List, Dict, Optional
import json

class LLMInterface:
    def __init__(self, model_name: str = "gpt-4-turbo"):
        self.model_name = model_name
        self.conversation_history = []

    def plan_task(self, goal: str, current_state: Dict) -> List[str]:
        """
        Generate a high-level plan for a given goal based on the current state.
        
        Args:
            goal (str): The objective (e.g., "Find ancient debris")
            current_state (dict): The agent's current status (pos, health, etc.)
            
        Returns:
            List[str]: A list of actionable steps or skills to execute.
        """
        prompt = self._construct_prompt(goal, current_state)
        
        # TODO: Implement actual API call to OpenAI/Gemini
        # response = self._call_api(prompt)
        
        # MOCK RESPONSE for testing
        print(f"[LLM Thinking] Goal: {goal}, State: {current_state}")
        return ["Action: LOOK_AROUND", "Action: WALK_FORWARD_5s", "Action: SAY_DONE"]

    def _construct_prompt(self, goal: str, state: Dict) -> str:
        return f"""
        You are a Minecraft Bedrock AI. 
        Current State: {json.dumps(state)}
        Goal: {goal}
        
        Generate a list of actions to execute.
        """
    
    def _call_api(self, prompt: str) -> str:
        # Placeholder for API request
        pass

if __name__ == "__main__":
    llm = LLMInterface()
    plan = llm.plan_task("Get Wood", {"position": (100, 64, 100)})
    print("Plan:", plan)
