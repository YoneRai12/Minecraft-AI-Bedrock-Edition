from typing import List, Dict, Optional
import json
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class LLMInterface:
    def __init__(self, model_name: str = "gemini-pro"):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            print("Warning: GOOGLE_API_KEY not found in .env. LLM will use fallback behavior.")
            self.model = None
        else:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            
    def plan_task(self, goal: str, current_state: Dict) -> List[str]:
        """
        Generate a plan using Gemini.
        Returns a list of skill strings (e.g. ["MOVE_FORWARD 5", "JUMP"]).
        """
        if not self.model:
             print("[LLM] Mocking response (No API Key)")
             return ["LOOK_AROUND", "MOVE_FORWARD 1", "JUMP"]

        prompt = self._construct_prompt(goal, current_state)
        
        try:
            response = self.model.generate_content(prompt)
            text = response.text
            # Simple parsing: expect a JSON list or line-by-line commands
            # For robustness, we ask for a JSON list of strings.
            return self._parse_response(text)
        except Exception as e:
            print(f"LLM Error: {e}")
            return []

    def _construct_prompt(self, goal: str, state: Dict) -> str:
        skills = ["MOVE_FORWARD <seconds>", "MOVE_BACKWARD <seconds>", "JUMP", "ATTACK <seconds>", "LOOK_AROUND", "WAIT <seconds>"]
        
        return f"""
        You are an autonomous Minecraft Agent.
        Your goal is: "{goal}"
        
        Current Status:
        - Position: {state.get('position', 'Unknown')}
        - Health: {state.get('health', 'Unknown')}
        
        Available Skills:
        {json.dumps(skills, indent=2)}
        
        Output a valid JSON list of strings representing the sequence of actions to achieve the goal.
        Do not output markdown code blocks, just the raw JSON.
        Example: ["MOVE_FORWARD 2", "JUMP", "ATTACK 1"]
        """

    def _parse_response(self, text: str) -> List[str]:
        # Cleanup markdown if present
        cleaned = text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:-3]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:-3]
            
        try:
            plan = json.loads(cleaned)
            if isinstance(plan, list):
                return plan
        except:
            print(f"Failed to parse LLM response: {text}")
        return []

if __name__ == "__main__":
    llm = LLMInterface()
    if llm.model:
        print("Testing Gemini connection...")
        plan = llm.plan_task("Jump twice", {"position": (0,0,0)})
        print("Plan:", plan)
    else:
        print("Skipping test (No API Key)")
