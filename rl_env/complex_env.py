import gymnasium as gym
from gymnasium import spaces
import numpy as np
import random
import json
import os

class ComplexEnv(gym.Env):
    def __init__(self):
        super().__init__()
        
        # --- 1. LOAD BOTH KNOWLEDGE SOURCES ---
        
        # Source A: Synthetic "Textbook" Knowledge from our original oracle
        synthetic_cases = []
        if os.path.exists("rl_env/oracle_data.json"):
            with open("rl_env/oracle_data.json") as f:
                synthetic_data = json.load(f)
                for item in synthetic_data:
                    item['source'] = 'synthetic' # Tag to identify the source
                    synthetic_cases.append(item)
        
        # Source B: Human-in-the-Loop "Real-World" Feedback
        human_feedback_cases = []
        feedback_file = "io/feedback.jsonl"
        if os.path.exists(feedback_file):
            with open(feedback_file, 'r') as f:
                for line in f:
                    try:
                        feedback = json.loads(line)
                        if not feedback or 'input' not in feedback or 'output' not in feedback:
                            continue
                            
                        # Safety check for None values
                        inp = feedback.get('input') or {}
                        outp = feedback.get('output') or {}
                        
                        params = inp.get('parameters')
                        if not params: continue
                        
                        location_map = {"urban": 0, "suburban": 1, "rural": 2}
                        loc_str = params.get('location', 'urban')
                        if loc_str not in location_map: loc_str = 'urban'
                        
                        state = [
                            float(params.get('plot_size', 0)), 
                            float(location_map[loc_str]), 
                            float(params.get('road_width', 0))
                        ]
                        
                        # The action the agent took that the human voted on
                        # Check if 'rl_optimal_action' exists
                        if 'rl_optimal_action' not in outp: continue
                        action_taken = outp['rl_optimal_action']
                        
                        human_feedback_cases.append({
                            "state": state,
                            "action_taken": action_taken,
                            "feedback": feedback.get('user_feedback', 'up'), # 'up' or 'down'
                            "source": 'human'
                        })
                    except Exception as e:
                        # Skip corrupted lines in the feedback file
                        # print(f"Skipping bad feedback line: {e}")
                        continue

        # Combine both knowledge sources into the final training set
        self.training_cases = synthetic_cases + human_feedback_cases
        
        if not self.training_cases:
            raise ValueError("No training data found. Please create oracle_data.json or provide feedback.")

        # --- 2. DEFINE SPACES ---
        self.action_space = spaces.Discrete(5) # 5 possible rule choices from the original design
        low_obs = np.array([0, 0, 0])
        high_obs = np.array([10000, 2, 100])
        self.observation_space = spaces.Box(low=low_obs, high=high_obs, dtype=np.float32)
        
        self.current_case = None
        print(f"ComplexEnv (HIRL) initialized with {len(self.training_cases)} total cases ({len(human_feedback_cases)} from human feedback).")
        
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        # Pick a new random case from our combined training data
        self.current_case = random.choice(self.training_cases)
        info = {}
        return np.array(self.current_case["state"]).astype(np.float32), info

    def step(self, action):
        # --- 3. IMPLEMENT THE NEW REWARD LOGIC ---
        source = self.current_case.get('source', 'synthetic')
        
        if source == 'human':
            # This case came from a human. Use the stronger +/- 2 reward.
            action_the_human_saw = self.current_case['action_taken']
            human_vote = self.current_case['feedback']
            
            # If the agent takes the same action that was UPVOTED
            if action == action_the_human_saw and human_vote == 'up':
                reward = 2  # Strong positive reward for agreeing with a good choice
            # If the agent takes the same action that was DOWNVOTED
            elif action == action_the_human_saw and human_vote == 'down':
                reward = -2 # Strong negative reward for repeating a bad choice
            # If the agent AVOIDS a downvoted action, that's good!
            elif action != action_the_human_saw and human_vote == 'down':
                reward = 1 # Small positive reward for avoiding a bad choice
            else:
                reward = 0 # Neutral reward for other scenarios
        else:
            # This is a synthetic case from the oracle. Use the original +/- 1 reward.
            correct_action = self.current_case["correct_action"]
            reward = 1 if action == correct_action else -1

        terminated = True
        truncated = False
        info = {}
        
        current_state = np.array(self.current_case["state"]).astype(np.float32)
        return current_state, reward, terminated, truncated, info