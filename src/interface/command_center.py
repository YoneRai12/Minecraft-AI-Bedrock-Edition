import threading
import queue
import time
from src.planning.llm_interface import LLMInterface
from src.core.state_manager import StateManager

class CommandCenter:
    def __init__(self, state_manager: StateManager):
        self.state_manager = state_manager
        self.llm = LLMInterface()
        self.command_queue = queue.Queue()
        self.active = True
        
    def start_input_thread(self):
        """Starts a thread to listen for console input."""
        t = threading.Thread(target=self._input_loop, daemon=True)
        t.start()
        print("Command Center Ready. Type commands (e.g., 'goal: Find diamond' or 'stop').")

    def _input_loop(self):
        while self.active:
            try:
                # Non-blocking input check is hard in pure Python console, 
                # so this thread blocks on input().
                cmd = input()
                self.process_command(cmd)
            except EOFError:
                break
    
    def process_command(self, cmd: str):
        if not cmd: return
        
        cmd = cmd.strip()
        print(f"[Command Received] {cmd}")
        
        if cmd.lower() == "stop":
            print("Stopping Command Center...")
            self.active = False
            # You might want to signal main.py to stop as well
            
        elif cmd.lower().startswith("goal:"):
            goal = cmd[5:].strip()
            self._handle_goal(goal)
            
        else:
            print("Unknown command. Try 'goal: <text>' or 'stop'.")

    def _handle_goal(self, goal: str):
        state = self.state_manager.get_state().__dict__
        plan = self.llm.plan_task(goal, state)
        print(f"Generated Plan: {plan}")
        # Here we would dispatch plan to a Skill Manager

if __name__ == "__main__":
    from src.core.state_manager import StateManager
    mgr = StateManager()
    cc = CommandCenter(mgr)
    cc.start_input_thread()
    
    while cc.active:
        time.sleep(1)
