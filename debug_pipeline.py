import os
import sys
from dotenv import load_dotenv
from logging_config import logger

# Mock System State
class MockState:
    def __init__(self):
        self.mcp_client = None
        self.llm = None
        self.rl_agent = None

def run_debug():
    print("=== STARTING PIPELINE DEBUG ===")
    
    # 1. Load Env
    load_dotenv()
    if not os.getenv("GEMINI_API_KEY"):
        print("ERROR: GEMINI_API_KEY is missing!")
        return

    # 2. Init Clients
    try:
        from mcp_client import MCPClient
        from langchain_google_genai import ChatGoogleGenerativeAI
        
        state = MockState()
        print("Initializing MCP Client...")
        state.mcp_client = MCPClient()
        
        print("Initializing LLM...")
        state.llm = ChatGoogleGenerativeAI(
            model="gemini-flash-latest",
            google_api_key=os.getenv("GEMINI_API_KEY")
        )

        print("Loading Trained RL Agent...")
        from stable_baselines3 import PPO
        model_path = "rl_env/ppo_hirl_agent.zip"
        if os.path.exists(model_path):
            state.rl_agent = PPO.load(model_path)
            print("RL Agent loaded successfully.")
        else:
            print("WARNING: RL Agent model not found.")
            state.rl_agent = None
        
    except Exception as e:
        print(f"CRITICAL INIT ERROR: {e}")
        import traceback
        traceback.print_exc()
        return

    # 3. Define Test Payload
    test_payload = {
        "project_id": "DEBUG_USER_CASE",
        "case_id": "case_suburbs_commercial",
        "city": "Mumbai",
        "document": "io/DCPR_2034.pdf",
        "parameters": {
            "plot_size": 800,
            "road_width": 10.0,
            "location": "Suburbs",
            "zoning": "Commercial (C-Zone)",
            "proposed_use": "Residential Building",
            "building_height": 14.0,
            "asr_rate": 90.0,
            "plot_deductions": 2.0
        }
    }

    # 4. Run Logic
    try:
        print("Invoking process_case_logic...")
        from main_pipeline import process_case_logic
        result = process_case_logic(test_payload, state)
        print("\n=== SUCCESS ===")
        print(result)
    except Exception as e:
        print("\n=== PIPELINE CRASHED ===")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_debug()
