import streamlit as st
import json
import os
import glob
import requests

# --- App Configuration ---
st.set_page_config(
    page_title="Multi-Agent Compliance System",
    layout="wide"
)
st.title("🤖 Multi-Agent AI System")
st.write("Select a case study, run the pipeline, and provide feedback to improve the system.")

# This is the single, official address of our professional backend service
API_BASE_URL = "http://127.0.0.1:8000"

# --- 1. UI for Case Selection ---
# NEW Inputs (Addressing User Request)
st.sidebar.markdown("---")
st.sidebar.markdown("**Detailed Parameters**")
zoning = st.sidebar.selectbox("Zoning Designation", ["Residential (R-Zone)", "Commercial (C-Zone)", "Industrial (I-Zone)", "Agriculture (Green Zone)", "Mixed-Use"], index=0)
proposed_use = st.sidebar.selectbox("Proposed Use", ["Residential Building", "Commercial Office", "IT Park", "Hotel/Hospital", "Industrial Unit", "Mixed-Use Building"], index=0)
building_height = st.sidebar.number_input("Proposed Height (m.)", min_value=0.0, value=15.0, help="Leave 0 if unknown")

# Refined Location Options
location_type = st.sidebar.selectbox("Location Type", ["Island City", "Suburbs", "Extended Suburbs", "Rest of Maharashtra"])

st.sidebar.markdown("**Advanced Constraints**")
asr_rate = st.sidebar.number_input("ASR Rate (₹/sq.m)", min_value=0.0, value=0.0, help="Annual Statement of Rates for Premium Calculation")
plot_deductions = st.sidebar.number_input("Area Deductions (sq.m)", min_value=0.0, value=0.0, help="Deductions for Road Widening/Reservations")

case_files = glob.glob("inputs/case_studies/*.json")
if not case_files:
    st.error("No case study files found in 'inputs/case_studies/'. Please create them first.")
else:
    case_options = {os.path.basename(f): f for f in case_files}
    selected_case_name = st.selectbox("Select a Case Study to Process:", options=list(case_options.keys()))

    # --- 2. Button to Trigger the API Call ---
    if st.button("🚀 Run Full Pipeline"):
        if selected_case_name:
            case_filepath = case_options[selected_case_name]
            
            with st.spinner(f"Sending '{selected_case_name}' to the API and waiting for analysis... This may take a few moments."):
                try:
                    # Load the case data to send as the API request body
                    with open(case_filepath, 'r') as f:
                        case_payload = json.load(f)
                    
                    if "parameters" not in case_payload: case_payload["parameters"] = {}
                    case_payload["parameters"]["zoning"] = zoning
                    case_payload["parameters"]["proposed_use"] = proposed_use
                    
                    # Update Location to match refined options
                    case_payload["parameters"]["location"] = location_type
                    
                    if building_height > 0:
                        case_payload["parameters"]["building_height"] = building_height
                    
                    # Inject Advanced Constraints
                    if asr_rate > 0:
                        case_payload["parameters"]["asr_rate"] = asr_rate
                    if plot_deductions > 0:
                        case_payload["parameters"]["plot_deductions"] = plot_deductions
                    
                    # --- THE CRUCIAL UPGRADE: Make a professional API Call ---
                    response = requests.post(f"{API_BASE_URL}/run_case", json=case_payload, timeout=300) # 5-minute timeout for long AI runs
                    
                    if response.status_code == 200:
                        # Store the clean JSON response from the API in the session state
                        st.session_state['report_data'] = response.json()
                        st.success("Pipeline complete! Analysis report received from the server.")
                    else:
                        st.error(f"API Error (Status {response.status_code}): The server returned an error. Details: {response.text}")
                        st.session_state['report_data'] = None

                except requests.exceptions.RequestException as e:
                    st.error(f"Connection Error: Could not connect to the API at {API_BASE_URL}. Is the server running? Details: {e}")
                    st.session_state['report_data'] = None

# --- 3. Display Results & Feedback ---
if st.session_state.get('report_data'):
    report_data = st.session_state['report_data']
    
    # Display the final, standardized report from the API
    if isinstance(report_data, str):
         # If report_data is a string, it is likely an error message from the backend
         st.error(report_data)
    else:
        st.subheader("✅ AI Analysis Report")
        st.markdown(report_data.get("entitlements", {}).get("analysis_summary", "No analysis report found."))
        
        # Display the confidence score from the bonus task!
        rl_decision = report_data.get("rl_decision", {})
        confidence = rl_decision.get("confidence_score")
        if confidence is not None:
            st.info(f"**RL Agent Confidence:** {confidence * 100:.0f}%")
    
    st.subheader("Was this analysis helpful?")
    col1, col2 = st.columns(2)

    def handle_feedback(feedback_type):
        """Sends the feedback to the /feedback endpoint of our API."""
        # The payload now correctly includes the project_id from the report
        payload = {
            "project_id": report_data.get("project_id", "unknown"),
            "case_id": report_data.get("case_id", "unknown"),
            "input_case": {
                "parameters": report_data.get("inputs", {})
            },
            "output_report": report_data,
            "user_feedback": feedback_type
        }
        try:
            response = requests.post(f"{API_BASE_URL}/feedback", json=payload, timeout=10)
            if response.status_code == 200:
                if feedback_type == "up":
                    st.success("Thank you! Your upvote has been recorded.")
                else:
                    st.error("Thank you! Your downvote has been recorded.")
            else:
                st.warning(f"Could not save feedback (API Status: {response.status_code}).")
        except requests.exceptions.RequestException:
            st.error("Connection Error: Could not send feedback to the API.")

    with col1:
        if st.button("👍 Yes (Upvote)", use_container_width=True):
            handle_feedback("up")
            
    with col2:
        if st.button("👎 No (Downvote)", use_container_width=True):
            handle_feedback("down")
