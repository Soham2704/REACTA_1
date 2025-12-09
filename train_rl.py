import os
import numpy as np
import gymnasium as gym
from gymnasium import spaces
from stable_baselines3 import PPO

# Define the environment inline to avoid import issues
class ComplianceEnv(gym.Env):
    def __init__(self):
        super(ComplianceEnv, self).__init__()
        # State: [Plot Size, Location (0-2), Road Width]
        self.observation_space = spaces.Box(low=0, high=10000, shape=(3,), dtype=np.float32)
        # Action: 0=Reject, 1=Approve w/ Conditions, 2=Approve Basic
        self.action_space = spaces.Discrete(3)
        
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.state = np.array([2000.0, 1.0, 15.0]).astype(np.float32)
        return self.state, {}
    
    def step(self, action):
        # Dummy reward logic for initialization
        reward = 1.0
        done = True
        return self.state, reward, done, False, {}

def train():
    print("Initializing Environment...")
    env = ComplianceEnv()
    
    print("Training PPO Agent...")
    model = PPO("MlpPolicy", env, verbose=1)
    model.learn(total_timesteps=2048)
    
    save_path = "rl_env/ppo_hirl_agent"
    print(f"Saving model to {save_path}...")
    model.save(save_path)
    print("DONE. Model saved.")

if __name__ == "__main__":
    train()
