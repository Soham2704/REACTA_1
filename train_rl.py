import os
import sys
import numpy as np
import gymnasium as gym
from stable_baselines3 import PPO

# Ensure we can import from rl_env
sys.path.append(os.path.join(os.path.dirname(__file__), "rl_env"))
from complex_env import ComplexEnv

def train():
    print("--- Training RL Agent on Live RAG Data ---")
    
    # 1. Initialize the Environment (loads oracle_data.json)
    try:
        env = ComplexEnv()
    except Exception as e:
        print(f"[FAIL] Could not initialize environment: {e}")
        return

    # 2. Train PPO Agent
    # We use MlpPolicy because inputs are simple vector [Plot, Location, Road]
    print("Training PPO Agent (MlpPolicy)...")
    model = PPO("MlpPolicy", env, verbose=1, learning_rate=0.0003, n_steps=128)
    
    # Train for enough steps to see convergence on the small dataset
    # 20 samples * 50 epochs approx = 1000 steps
    model.learn(total_timesteps=5000)
    
    # 3. Save the Model
    save_dir = "rl_env"
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, "ppo_hirl_agent")
    
    print(f"Saving model to {save_path}...")
    model.save(save_path)
    print("DONE. Model saved.")

if __name__ == "__main__":
    train()
