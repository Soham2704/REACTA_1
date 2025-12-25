import json
import os
import uvicorn
from fastapi import FastAPI, HTTPException, Response, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
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

# --- 5. WebSocket & Logging Infrastructure (Real-Time Updates) ---
from fastapi import WebSocket, WebSocketDisconnect
import logging
import asyncio

class ConnectionManager:
    """Manages active WebSocket connections for log broadcasting."""
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total: {len(self.active_connections)}")

    async def broadcast(self, message: str):
        """Sends a message to all connected clients."""
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Failed to send to WS: {e}")

manager = ConnectionManager()

# Global variable to hold the main event loop
main_loop = None

class WebSocketLogHandler(logging.Handler):
    """Intercepts standard logs and pushes them to the WebSocket manager."""
    def emit(self, record):
        try:
            # Filter out noise (boring logs)
            msg = record.getMessage()
            if "Received /" in msg or "Input Parameters" in msg:
                 return
            
            # Use explicit type if provided in extra={'type': '...'}
            msg_type = getattr(record, 'type', None)
            
            # Fallback heuristics
            if not msg_type:
                if "MCP" in msg or "VectorDB" in msg or "Rules" in msg: msg_type = 'rag'
                elif "LLM" in msg or "AI Consultant" in msg: msg_type = 'llm'
                elif "RL" in msg or "Policy" in msg: msg_type = 'rl'
                elif "Complete" in msg or "Success" in msg: msg_type = 'success'
                else: msg_type = 'info'
            
            payload = json.dumps({
                "type": msg_type,
                "text": msg,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Broadcast asynchronously
            if main_loop and main_loop.is_running():
                asyncio.run_coroutine_threadsafe(manager.broadcast(payload), main_loop)
            else:
                 # Fallback for debugging if loop isn't ready
                 pass 

        except Exception:
            self.handleError(record)

# --- 6. Server Startup & Shutdown Events ---
@app.on_event("startup")
async def startup_event():
    """This function runs ONCE when the server starts up to initialize components."""
    logger.info("Server starting up...")
    
    # 0. Capture Main Loop for Thread-Safe Logging
    global main_loop
    main_loop = asyncio.get_running_loop()
    
    # 1. Attach WebSocket Handler to Our Specific Logger
    # We must attach to 'logger' because propagate=False in logging_config.py
    ws_handler = WebSocketLogHandler()
    ws_handler.setFormatter(logging.Formatter('%(message)s'))
    logger.addHandler(ws_handler)
    
    # 2. Init AI Models
    from langchain_google_genai import ChatGoogleGenerativeAI
    
    load_dotenv()
    os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY")

    state.mcp_client = MCPClient()
    
    try:
        if not os.getenv("GEMINI_API_KEY"):
            logger.warning("GEMINI_API_KEY not found in .env. AI features will be disabled.")
            state.llm = None
        else:
            state.llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
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
    logger.info("All components and Real-Time Logging initialized.")

@app.on_event("shutdown")
def shutdown_event():
    if state.mcp_client:
        state.mcp_client.close()

# --- 7. API Endpoints ---
@app.websocket("/ws/logs")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # We just hold the connection open; messages are pushed by the LogHandler
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
@app.post("/run_case", summary="Run the full compliance pipeline for a single case")
def run_case_endpoint(case_input: CaseInput):
    logger.info(f"Received /run_case request for case {case_input.case_id}")
    logger.info(f"Input Parameters: {case_input.parameters.dict()}")

    if not state.is_initialized:
        logger.error("System state is not initialized.")
        raise HTTPException(status_code=503, detail="System is initializing. Please try again.")
    try:
        result = process_case_logic(case_input.dict(), state)
        logger.info(f"Case {case_input.case_id} processed successfully.")
        return result
    except Exception as e:
        logger.error(f"Error in /run_case: {e}", exc_info=True)
        # Return the actual error message to the frontend for debugging
        raise HTTPException(status_code=500, detail=f"Pipeline Error: {str(e)}")

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

# --- 9. Serve React Frontend (Static Files) ---
# Check if static directory exists (it will in Docker)
if os.path.exists("./static"):
    app.mount("/assets", StaticFiles(directory="./static/assets"), name="assets")
    # We might need to mount other root-level files like favicon.ico if they exist
    # SPA Fallback: catching any other route and serving index.html
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # Check if file exists in static folder corresponding to path (e.g. favicon.ico)
        static_file = os.path.join("static", full_path)
        if os.path.exists(static_file) and os.path.isfile(static_file):
            return FileResponse(static_file)
        # Otherwise serve index.html
        return FileResponse("static/index.html")
else:
    logger.warning("Static directory not found. Frontend will not be served.")
# --- 8. Main execution block for running the server ---
if __name__ == "__main__":
    print("--- Starting MCP-Integrated API Server with Uvicorn ---")
    print("Access the interactive API docs at http://127.0.0.1:8000/docs")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

