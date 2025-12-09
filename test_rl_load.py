import os
import sys
from stable_baselines3 import PPO

print("Current Working Directory:", os.getcwd())
model_path = "rl_env/ppo_hirl_agent.zip"

if not os.path.exists(model_path):
    print(f"ERROR: File not found at {model_path}")
    sys.exit(1)

try:
    print(f"Attempting to load {model_path}...")
    model = PPO.load(model_path)
    print("SUCCESS: Model loaded.")
except Exception as e:
    print(f"FAILURE: Could not load model.")
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
