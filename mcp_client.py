from chroma_client import ChromaDBClient
from typing import List, Dict, Any
import json
import os
from datetime import datetime
import uuid

class MCPClient:
    """
    A client for interacting with the Managed Compliance Platform.
    Now backed by ChromaDB for vector-search enabled rule management.
    """
    def __init__(self):
        self.db = ChromaDBClient()
        print("MCPClient initialized, connected to ChromaDB.")

    def add_rule(self, rule_data: Dict[str, Any]):
        """Adds a new rule to the MCP, checking for duplicates."""
        # De-duplication is now handled by ChromaDB's UPSERT (based on ID)
        # But we can still return True/False if needed, though upsert always succeeds technically.
        try:
            return self.db.add_rule(rule_data)
        except Exception as e:
            print(f"Error adding rule: {e}")
            return False

    def query_rules(self, city: str, parameters: dict) -> List[Dict[str, Any]]:
        """
        Finds all rules that match the given case parameters.
        Delegates to ChromaDB's structured filtering.
        """
        return self.db.query_rules(city, parameters)

    def add_feedback(self, feedback_data: Dict[str, Any]):
        """
        Persists user feedback. In a full MCP, this would write to a 'feedback' table.
        For now, it writes to the required feedback.jsonl file.
        """
        # Ensure directory exists
        os.makedirs("io", exist_ok=True)
        log_file = "io/feedback.jsonl"
        
        input_payload = feedback_data.get("input_case", {})
        output_payload = feedback_data.get("output_report", {})
        
        # Extract meaningful summary data to keep the log clean
        # If output is a dict (standard), get entitlements/analysis. If string (legacy/error), use as is.
        report_text = ""
        if isinstance(output_payload, dict):
            # Try to grab the text report
            entitlements = output_payload.get("entitlements", {})
            if isinstance(entitlements, dict):
                 report_text = entitlements.get("analysis_summary", "")
            else:
                 report_text = str(output_payload)
        else:
            report_text = str(output_payload)

        feedback_record = {
            "feedback_id": str(uuid.uuid4()),
            "project_id": feedback_data.get("project_id"),
            "case_id": feedback_data.get("case_id"),
            "user_feedback": feedback_data.get("user_feedback"),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            # FULL CONTEXT FOR RL
            "input": input_payload,
            "output": output_payload,
            "query_parameters": input_payload.get("parameters", {}),
            "report_excerpt": report_text[:500] + "..." if len(report_text) > 500 else report_text 
        }
        try:
            with open(log_file, "a") as f:
                f.write(json.dumps(feedback_record) + "\n")
            return feedback_record
        except Exception as e:
            print(f"Error saving feedback: {e}")
            return None

    def close(self):
        """Closes the database session."""
        # ChromaDB client doesn't strictly need closing in this context, 
        # but we can print a message.
        print("MCPClient session ended.")
