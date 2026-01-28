import os
import json
from openai import OpenAI
from dotenv import load_dotenv

class LLMInterface:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("GOOGLE_API_KEY", "local") # Dummy key for local
        self.base_url = os.getenv("LLM_API_BASE", "http://localhost:1234/v1")
        self.model_name = os.getenv("LLM_MODEL", "mistralai/ministral-3-14b-reasoning")
        
        print(f"[LLM] Connecting to {self.base_url} (Model: {self.model_name})...")
        
        try:
            self.client = OpenAI(base_url=self.base_url, api_key=self.api_key)
            # Test connection?
            # self.client.models.list()
        except Exception as e:
            print(f"[LLM] Connection Error: {e}")
            self.client = None

    def get_plan(self, goal: str, state_summary: str, available_skills: list) -> list:
        """
        Generate a plan using Local LLM (OpenAI Compatible).
        """
        if not self.client:
            print("[LLM] Mocking plan (No Client)")
            return ["LOOK_AROUND", "WAIT 1"]

        prompt = f"""
        You are a Minecraft Agent.
        GOAL: {goal}
        STATE: {state_summary}
        SKILLS: {', '.join(available_skills)}
        
        Task: Break down the GOAL into a list of skill actions.
        Format: Return ONLY a JSON list of strings. Example: ["MOVE_FORWARD 2", "JUMP"]
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful Minecraft AI assistant. Reply only in JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=200
            )
            
            content = response.choices[0].message.content.strip()
            print(f"[LLM] Raw Response: {content}")
            
            # Simple parsing (try to find JSON list)
            start = content.find('[')
            end = content.rfind(']') + 1
            if start != -1 and end != -1:
                json_str = content[start:end]
                return json.loads(json_str)
            else:
                print(f"[LLM] Could not find JSON in response.")
                return []
                
        except Exception as e:
            print(f"[LLM] Inference Error: {e}")
            return []
