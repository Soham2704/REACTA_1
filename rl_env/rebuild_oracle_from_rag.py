
import os
import json
import random
import numpy as np
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from chroma_client import ChromaDBClient

# Configuration
NUM_SAMPLES = 20
OUTPUT_FILE = "rl_env/oracle_data.json"

def get_teacher_decision(llm, context_text, parameters):
    """
    Asks the LLM 'Teacher' to decide the optimal action based on the retrieved rules.
    Actions (0-4):
    0: Reject (Not allowed)
    1: Low FSI (Residential, Small Road)
    2: Medium FSI (Standard)
    3: High FSI (Road > 15m)
    4: Premium FSI (High Rise, TDR applicable)
    """
    
    prompt = PromptTemplate.from_template("""
    You are an Expert City Planner acting as a 'Teacher' for a Reinforcement Learning agent.
    
    Context Rules:
    {context}
    
    Scenario Parameters:
    - Plot Size: {plot_size} sq.m
    - Road Width: {road_width} m
    - Location: {location}
    
    Task: Decide the Best Development Strategy (Action 0-4).
    
    Actions:
    0: Reject (Plot too small or unsafe)
    1: Low Density (Basic FSI ~1.0)
    2: Medium Density (FSI ~1.5 - 2.0)
    3: High Density (FSI ~2.5 - 3.0, requires wide road)
    4: Premium / High Rise (FSI > 3.0, requires very wide road)
    
    Logic Guide:
    - If Road < 9m -> Action 1 (Low)
    - If Road 9-12m -> Action 2 (Medium)
    - If Road 12-18m -> Action 3 (High)
    - If Road > 18m -> Action 4 (Premium)
    - If specific rules in Context forbid construction -> Action 0
    
    Return ONLY the Action Number (0, 1, 2, 3, or 4).
    """)
    
    chain = prompt | llm
    try:
        res = chain.invoke({
            "context": context_text,
            "plot_size": parameters["plot_size"],
            "road_width": parameters["road_width"],
            "location": parameters["location"]
        })
        text = res.content.strip()
        # Extract first digit found
        import re
        match = re.search(r'\d', text)
        if match:
            return int(match.group())
        return 1 # Default conservative
    except Exception as e:
        print(f"Teacher failed: {e}")
        return 1

def rebuild_oracle():
    print(f"--- Rebuilding Oracle from Live RAG Data ({NUM_SAMPLES} samples) ---")
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        # Fallback for some shell environments
        api_key = os.environ.get("GEMINI_API_KEY")
        
    # Init Components
    # Using correct model from previous fix
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.0, google_api_key=api_key)
    db_client = ChromaDBClient()
    
    new_data = []
    
    cities = ["Nashik", "Pune", "Mumbai"]
    locations = ["urban", "suburban", "rural"]
    loc_map = {"urban": 0, "suburban": 1, "rural": 2}
    
    for i in range(NUM_SAMPLES):
        # 1. Generate Random Scenario
        city = random.choice(cities)
        plot_size = random.randint(300, 5000)
        road_width = random.choice([6.0, 7.5, 9.0, 12.0, 15.0, 18.0, 24.0, 30.0])
        location = random.choice(locations)
        
        print(f"Sample {i+1}: {city}, Road {road_width}m, Plot {plot_size}m2")
        
        # 2. Query RAG (The "Real" Knowledge)
        params = {
            "road_width_m": road_width,
            "plot_area_sqm": plot_size,
            "location": location
        }
        rules = db_client.query_rules(city, params)
        
        # Consolidate context for Teacher
        context_str = ""
        for r in rules:
            context_str += f"- {r.get('notes', '')}\n"
            if 'entitlements' in r:
                context_str += f"  Entitlements: {r['entitlements']}\n"
        
        if not context_str:
            context_str = "No specific rules found. Use general logic."
            
        # 3. Ask Teacher
        # Remap for consistency
        teacher_params = {
            "plot_size": plot_size,
            "road_width": road_width,
            "location": location
        }
        correct_action = get_teacher_decision(llm, context_str, teacher_params)
        print(f"  -> Teacher Decision: Action {correct_action}")
        
        # 4. Save
        new_data.append({
            "state": [plot_size, loc_map[location], road_width],
            "correct_action": correct_action,
            "city_context": city # Extra metadata potentially useful later
        })

    # Write to file
    with open(OUTPUT_FILE, "w") as f:
        json.dump(new_data, f, indent=4)
        
    print(f"\n[SUCCESS] New Oracle Data saved to {OUTPUT_FILE}")
    print("The RL agent is now ready to train on this grounded data.")

if __name__ == "__main__":
    rebuild_oracle()
