import json
import os
import uvicorn
from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from typing import List, Dict, Any
from datetime import datetime
import uuid

# --- Import our logger, the NEW MCP Client, and the pipeline logic ---
# --- Import our logger, the NEW MCP Client, and the pipeline logic ---
from logging_config import logger
from mcp_client import MCPClient
from main_pipeline import process_case_logic
# Removed Rule import as we are no longer using SQLAlchemy

# --- 3. Data Models for API (The "Contract") ---
from typing import List, Dict, Any, Optional

class CaseParameters(BaseModel):
    plot_size: int
    location: str
    road_width: float
    # New detailed parameters (Optional for backward compatibility)
    zoning: Optional[str] = None
    proposed_use: Optional[str] = None
    building_height: Optional[float] = None
    # Advanced Financial & Physical Constraints
    asr_rate: Optional[float] = None
    plot_deductions: Optional[float] = None

class CaseInput(BaseModel):
    project_id: str
    case_id: str
    city: str
    document: str
    parameters: CaseParameters

class FeedbackInput(BaseModel):
    project_id: str
    case_id: str
    user_feedback: str = Field(..., pattern="^(up|down)$")
    # Added to support full logging
    input_case: Optional[Dict[str, Any]] = {}
    output_report: Optional[Dict[str, Any]] = {}

# --- 1. Create the FastAPI App ---
app = FastAPI(
    title="Multi-Agent Compliance System API",
    description="An API for running a multi-agent pipeline, managing feedback, and integrating with the AI Design Platform."
)

# --- 2. Add CORS Middleware for Team Integration ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, this would be a specific list of allowed domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# --- 4. Global State to hold our "brains" and the MCP Client ---
class SystemState:
    def __init__(self):
        self.mcp_client: MCPClient = None
        self.llm = None
        self.rl_agent = None
        # The other agents are now stateless and will be created in the pipeline
        self.is_initialized = False

state = SystemState()

# --- 5. Server Startup & Shutdown Events ---
@app.on_event("startup")
def startup_event():
    """This function runs ONCE when the server starts up to initialize the MCP client and models."""
    logger.info("Server starting up... Initializing MCP Client and AI models.")
    from langchain_google_genai import ChatGoogleGenerativeAI
    from stable_baselines3 import PPO

    load_dotenv()
    os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY")

    state.mcp_client = MCPClient()
    
    try:
        if not os.getenv("GEMINI_API_KEY"):
            logger.warning("GEMINI_API_KEY not found in .env. AI features will be disabled.")
            state.llm = None
        else:
            # Use gemini-1.5-flash for better free-tier performance and higher rate limits
            state.llm = ChatGoogleGenerativeAI(
                model="gemini-flash-latest",
                google_api_key=os.getenv("GEMINI_API_KEY"),
                max_retries=3,
                request_timeout=60
            )
    except Exception as e:
        logger.error(f"Failed to initialize LLM: {e}")
        state.llm = None

    try:
        from stable_baselines3 import PPO
        state.rl_agent = PPO.load("rl_env/ppo_hirl_agent.zip")
    except Exception as e:
        logger.error(f"Failed to load RL agent: {e}")
        state.rl_agent = None
    
    state.is_initialized = True
    logger.info("All components and MCP Client initialized successfully. Server is ready.")

@app.on_event("shutdown")
def shutdown_event():
    """This function runs ONCE when the server shuts down to close connections."""
    if state.mcp_client:
        state.mcp_client.close()

# --- 6. API Endpoints ---
@app.post("/run_case", summary="Run the full compliance pipeline for a single case")
def run_case_endpoint(case_input: CaseInput):
    if not state.is_initialized:
        raise HTTPException(status_code=503, detail="System is initializing. Please try again.")
    try:
        return process_case_logic(case_input.dict(), state)
    except Exception as e:
        logger.error(f"Error in /run_case: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/feedback", summary="Submit feedback for a processed case")
def feedback_endpoint(feedback: FeedbackInput):
    if not state.is_initialized:
        raise HTTPException(status_code=503, detail="System is initializing.")
    try:
        # Correctly use the MCP Client to handle feedback
        feedback_record = state.mcp_client.add_feedback(feedback.dict())
        logger.info(f"Feedback saved via MCP for case {feedback.case_id}")
        return {"status": "success", "feedback_id": feedback_record["feedback_id"]}
    except Exception as e:
        logger.error(f"Error in /feedback: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Could not save feedback.")

@app.get("/logs/{case_id}", summary="Get all agent logs for a specific case_id")
def logs_endpoint(case_id: str) -> List[Dict[str, Any]]:
    log_file = "reports/agent_log.jsonl"
    case_logs = []
    if not os.path.exists(log_file):
        raise HTTPException(status_code=404, detail=f"Log file not found.")
    try:
        with open(log_file, 'r') as f:
            for line in f:
                log_entry = json.loads(line)
                log_case_data = log_entry.get('extra_data', {}).get('case', {})
                if log_case_data and log_case_data.get('case_id') == case_id:
                    case_logs.append(log_entry)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading log file: {e}")
    return case_logs

@app.get("/get_rules", summary="Fetches parsed rule JSON for a given city")
def get_rules(city: str) -> List[Dict[str, Any]]:
    if not state.is_initialized:
        raise HTTPException(status_code=503, detail="System is initializing.")
    try:
        # Use the MCP Client to query rules for the city
        # We pass an empty parameters dict to get all rules for the city
        rules_from_db = state.mcp_client.query_rules(city, {})
        
        # They are already dictionaries, so we can return them directly
        return rules_from_db
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not fetch rules: {e}")

@app.get("/get_geometry/{project_id}/{case_id}", summary="Serves the generated STL geometry file")
def get_geometry(project_id: str, case_id: str):
    file_path = f"outputs/projects/{project_id}/{case_id}_geometry.stl"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Geometry file not found.")
    return FileResponse(file_path, media_type='application/vnd.ms-pki.stl', filename=f"{case_id}.stl")

@app.get("/get_feedback_summary", summary="Returns aggregated thumbs up/down stats")
def get_feedback_summary():
    feedback_file = "io/feedback.jsonl"
    summary = {"upvotes": 0, "downvotes": 0, "total_feedback": 0}
    if not os.path.exists(feedback_file):
        return summary
    try:
        with open(feedback_file, 'r') as f:
            for line in f:
                try:
                    feedback = json.loads(line)
                    if feedback.get("user_feedback") == "up":
                        summary["upvotes"] += 1
                    elif feedback.get("user_feedback") == "down":
                        summary["downvotes"] += 1
                    summary["total_feedback"] += 1
                except json.JSONDecodeError:
                    continue
    except Exception as e:
        raise HTTPException(status_code=500, detail="Could not process feedback file.")
    return summary
    
@app.get("/projects/{project_id}/cases", summary="Get all case results for a specific project")
def get_project_cases(project_id: str) -> List[Dict[str, Any]]:
    """
    Searches the output directory and returns a list of all report.json files
    associated with the given project_id.
    """
    project_dir = f"outputs/projects/{project_id}"
    if not os.path.exists(project_dir):
        # Return an empty list if the project folder doesn't exist, which is a valid case.
        return []
    
    project_reports = []
    try:
        for filename in os.listdir(project_dir):
            if filename.endswith("_report.json"):
                with open(os.path.join(project_dir, filename), 'r') as f:
                    project_reports.append(json.load(f))
    except Exception as e:
        logger.error(f"Error reading reports for project {project_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error reading project reports.")
    return project_reports
# --- 8. Main execution block for running the server ---
if __name__ == "__main__":
    print("--- Starting MCP-Integrated API Server with Uvicorn ---")
    print("Access the interactive API docs at http://127.0.0.1:8000/docs")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

