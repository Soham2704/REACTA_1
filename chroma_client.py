import chromadb
from chromadb.config import Settings
import uuid
import os
import json
from typing import List, Dict, Any, Optional

class ChromaDBClient:
    """
    Client for interacting with ChromaDB.
    replaces the SQL-based MCPClient for rule storage and retrieval.
    """
    def __init__(self, persist_directory: str = None):
        if persist_directory is None:
            persist_directory = os.getenv("CHROMADB_PERSIST_DIRECTORY", "rules_chroma_db")
        self.persist_directory = persist_directory
        # Ensure directory exists
        os.makedirs(persist_directory, exist_ok=True)
        
        print(f"--- Initializing ChromaDB Client at '{persist_directory}' ---")
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Create or get the collection for rules
        self.collection = self.client.get_or_create_collection(name="rules")
        print("ChromaDB 'rules' collection ready.")

    def add_rule(self, rule_data: Dict[str, Any], document_content: Optional[str] = None, **kwargs):
        """
        Adds a rule to the ChromaDB collection.
        
        Args:
            rule_data: Dictionary containing rule details (id, city, conditions, entitlements, etc.)
            document_content: The actual text content to embed. If None, uses 'notes' or a generic string.
        """
        rule_id = rule_data.get("id")
        if not rule_id:
            print("Error: Rule missing 'id'. Cannot add to ChromaDB.")
            return False

        # Prepare metadata - Flatten nested structures for filtering
        # ChromaDB metadata must be int, float, str, or bool. No nested dicts.
        metadata = {
            "id": rule_id,
            "city": rule_data.get("city", "Unknown"),
            "rule_type": rule_data.get("rule_type", "General"),
            "notes": rule_data.get("notes", ""),
            "page_number": kwargs.get("page_number", 0), # Store page number in metadata
            # Store the full JSON string so we can reconstruct the object later
            "full_json": json.dumps(rule_data) 
        }

        # Flatten conditions for filtering
        conditions = rule_data.get("conditions", {})
        
        # handle road width
        if "road_width_m" in conditions:
            rw = conditions["road_width_m"]
            if isinstance(rw, dict):
                if "min" in rw: metadata["road_width_min"] = float(rw["min"])
                if "max" in rw: metadata["road_width_max"] = float(rw["max"])
        
        # handle plot area
        if "plot_area_sqm" in conditions:
            pa = conditions["plot_area_sqm"]
            if isinstance(pa, dict):
                if "min" in pa: metadata["plot_area_min"] = float(pa["min"])
                if "max" in pa: metadata["plot_area_max"] = float(pa["max"])
                
        # Handle simple equality conditions
        for key, value in conditions.items():
            if isinstance(value, (str, int, float, bool)):
                 metadata[f"condition_{key}"] = value

        # Use provided content or fallback to notes/description
        if not document_content:
            document_content = rule_data.get("notes", f"Rule {rule_id} for {metadata['city']}")

        try:
            self.collection.upsert(
                ids=[rule_id],
                metadatas=[metadata],
                documents=[document_content]
            )
            return True
        except Exception as e:
            print(f"Error adding rule {rule_id} to ChromaDB: {e}")
            return False

    def query_rules(self, city: str, parameters: dict, n_results: int = 10) -> List[Dict[str, Any]]:
        """
        Query rules based on city and parameters.
        Uses ChromaDB's where clause for structured filtering.
        """
        where_clauses = []
        
        # 1. City Filter
        where_clauses.append({"city": city})

        # 2. Road Width Filter (if provided)
        # We want rules where: rule_min <= param_width < rule_max
        if "road_width_m" in parameters:
            width = float(parameters["road_width_m"])
            # In ChromaDB, we can't easily do "value BETWEEN field_min AND field_max" purely in 'where' 
            # if we are comparing a scalar param against stored range fields.
            # Wait, ChromaDB 'where' compares Metadata Field vs Value.
            # We have metadata: road_width_min, road_width_max.
            # We want: road_width_min <= width AND road_width_max > width.
            # So: {"road_width_min": {"$lte": width}} AND {"road_width_max": {"$gt": width}}
            
            where_clauses.append({"road_width_min": {"$lte": width}})
            where_clauses.append({"road_width_max": {"$gt": width}})

        # 3. Plot Area Filter (if provided)
        if "plot_area_sqm" in parameters:
            area = float(parameters["plot_area_sqm"])
            where_clauses.append({"plot_area_min": {"$lte": area}})
            where_clauses.append({"plot_area_max": {"$gte": area}})

        # Construct final where clause
        if len(where_clauses) == 1:
            final_where = where_clauses[0]
        elif len(where_clauses) > 1:
            final_where = {"$and": where_clauses}
        else:
            final_where = {}

        print(f"Querying ChromaDB with where: {final_where}")
        
        try:
            # 1. Structured Search (Primary)
            results = self.collection.query(
                query_texts=[""], 
                n_results=n_results,
                where=final_where
            )
            
            found_rules = []
            if results["metadatas"] and results["metadatas"][0]:
                for i, meta in enumerate(results["metadatas"][0]):
                    rule_obj = {}
                    if "full_json" in meta:
                        try:
                            rule_obj = json.loads(meta["full_json"])
                        except: pass
                    
                    if results["documents"] and results["documents"][0][i]:
                         doc_content = results["documents"][0][i]
                         # Only overwrite 'notes' if this is a RawText chunk (unstructured)
                         # For structured rules, we prefer the AI-generated 'notes' (summary), 
                         # but we attach the full text as 'source_evidence' for reference.
                         if rule_obj.get("rule_type") == "RawText":
                             rule_obj["notes"] = doc_content
                         else:
                             rule_obj["source_evidence"] = doc_content

                    # Inject page_number from metadata if available
                    if "page_number" in meta:
                         rule_obj["page_number"] = meta["page_number"]

                    if rule_obj:
                        found_rules.append(rule_obj)

            # 2. Semantic Fallback (If strictly structured search yields too few results,
            #    or if we are likely dealing with RawText chunks that lack metadata)
            if len(found_rules) < n_results:
                print("Structured search yielded low results. Attempting Semantic Search...")
                
                # Construct a natural language query from parameters
                # Construct a natural language query from parameters
                # ENHANCED QUERY: Auto-adapt terminology based on city
                if city == "Delhi":
                     # Delhi uses FAR, Ground Coverage, MPD-2021 terms
                     nl_query = f"Master Plan Delhi MPD 2021 zoning regulations residential plot development controls FAR Floor Area Ratio Ground Coverage max height setbacks parking standards for {city}"
                else:
                     # Mumbai/Pune/Nashik use FSI, Fungible, TDR terms
                     nl_query = f"Zoning rules FSI floor space index permissible height setbacks side margin rear margin premium FSI rate exclusions parking requirements fungible compensatory area FCA for {city}"

                if "road_width_m" in parameters:
                    nl_query += f" with road width {parameters['road_width_m']} meters"
                if "plot_area_sqm" in parameters:
                    nl_query += f" and plot area {parameters['plot_area_sqm']} sq m"
                if "location" in parameters:
                    nl_query += f" in {parameters['location']}"
                
                # Add explicit keywords to boost retrieval
                if city == "Delhi":
                    nl_query += " residential group housing plotting MPD"
                else:
                    nl_query += " entitlements residential commercial generic"
                
                print(f"Semantic Query: '{nl_query}'")
                
                semantic_results = self.collection.query(
                    query_texts=[nl_query],
                    n_results=n_results,
                    # We can't really use the same strict 'where' if metadata is missing.
                    # We might filter just by city if possible.
                    where={"city": city}
                )
                
                if semantic_results["metadatas"] and semantic_results["metadatas"][0]:
                     for i, meta in enumerate(semantic_results["metadatas"][0]):
                        # If it's a RawText chunk, treat it as a rule
                        if meta.get("rule_type") == "RawText":
                            found_rules.append({
                                "id": meta.get("id"),
                                "city": meta.get("city"),
                                "rule_type": "RawText",
                                "conditions": {},
                                "entitlements": {},
                                "notes": semantic_results["documents"][0][i] # Use the actual text content
                            })
                        elif "full_json" in meta:
                             try:
                                r = json.loads(meta["full_json"])
                                # Avoid duplicates (simple check by ID)
                                if not any(existing['id'] == r['id'] for existing in found_rules):
                                    found_rules.append(r)
                             except: pass

            return found_rules

        except Exception as e:
            print(f"Error querying ChromaDB: {e}")
            return []
            
    def count(self):
        return self.collection.count()
        
    def peek(self):
        return self.collection.peek()
