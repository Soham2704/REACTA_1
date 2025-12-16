import json
import os
import argparse
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from chroma_client import ChromaDBClient
from tqdm import tqdm
import concurrent.futures
import uuid

# --- SETUP & PROMPT (UNCHANGED) ---
load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY") 
# Configure GenAI to ignore warnings if necessary or set specific transport options if needed.

EXTRACTION_PROMPT ="""
You are a hyper-precise AI data analyst. Your sole task is to read a block of unstructured text from a regulatory document and extract any specific, quantifiable rules into a structured JSON format.

**Your Target JSON Schema:**
You must extract rules into a list of JSON objects, where each object has the following keys: "id", "city", "rule_type", "conditions", "entitlements", "notes".

1.  **id**: A unique ID you generate, like "MUM-FSI-002".
2.  **city**: The city the rule applies to (e.g., "Mumbai").
3.  **rule_type**: A camel-case category (e.g., "FSI", "Setback", "BuildingHeight").
4.  **conditions**: A JSON object describing the "IF" part of the rule. Use keys like "road_width_m", "plot_area_sqm", "location_type", "zone". For numerical conditions, use `{{ "min": X, "max": Y }}`.
5.  **entitlements**: A JSON object describing the "THEN" part of the rule. Use keys like "base_fsi", "total_fsi", "max_height_m", "los_percentage".
6.  **notes**: A brief, human-readable summary of the rule.

**Example of a Perfect Output:**
```json
[
  {{
    "id": "MUM-FSI-001",
    "city": "Mumbai",
    "rule_type": "FSI",
    "conditions": {{
      "location_type": ["Suburbs", "Extended Suburbs"],
      "road_width_m": {{"min": 18, "max": 27}}
    }},
    "entitlements": {{
      "total_fsi": 2.4
    }},
    "notes": "FSI for Suburbs on 18m-27m roads."
  }}
]
```

**Instructions:**
* Analyze the <TEXT_BLOCK> provided below.
* If you find one or more clear, quantifiable rules, extract them into the JSON list format.
* **If you find NO specific, quantifiable rules, you MUST return an empty list: `[]`**. Do not invent rules.

<TEXT_BLOCK>
{text_chunk}
</TEXT_BLOCK>
"""

# --- RULE EXTRACTION AGENT (UNCHANGED) ---
class RuleExtractionAgent:
    def __init__(self):
        # Enable the LLM for rule extraction
        try:
            self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.0)
            self.prompt = PromptTemplate.from_template(EXTRACTION_PROMPT)
            self.chain = self.prompt | self.llm
            self.offline_mode = False
            print("[CONFIG] AI Rule Extraction ENABLED (Gemini 2.5 Flash).")
        except Exception as e:
            print(f"[{e}] LLM Init failed. Switching to OFFLINE PASSTHROUGH MODE.")
            self.offline_mode = True
    
    def extract_rules_from_text(self, text_chunk: str, city: str):
        if self.offline_mode:
            # Return a single dummy rule that wraps the content for Vector Search
            return [{
                "id": f"RAW-CHUNK-{uuid.uuid4()}", # Unique ID for every chunk
                "city": city,
                "rule_type": "RawText",
                "conditions": {},
                "entitlements": {},
                "notes": "Raw PDF content indexed for search.",
            }]


        try:
            response = self.chain.invoke({"text_chunk": text_chunk})
            json_str = response.content.strip()
            start_index = json_str.find('[')
            end_index = json_str.rfind(']') + 1
            if start_index != -1 and end_index != 0:
                json_str = json_str[start_index:end_index]
                extracted_data = json.loads(json_str)
                for rule in extracted_data:
                    if 'city' not in rule: rule['city'] = city
                return extracted_data
            else: 
                raise ValueError("JSON parsing failed or empty")
        except Exception as e:
            # Fallback to RAW CHUNK if LLM fails at runtime (e.g. invalid key)
            print(f"Extraction failed for chunk. Fallback to Raw Indexing. Error: {e}")
            return [{
                "id": f"FALLBACK-CHUNK-{uuid.uuid4()}", 
                "city": city,
                "rule_type": "RawText",
                "conditions": {},
                "entitlements": {},
                "notes": "Raw PDF content (Fallback due to AI error).",
            }]

def process_page(page_data, city_name, agent):
    # Extract page number and content
    text_content = page_data.get('content', '')
    page_num = page_data.get('page', 0) # Default to 0 if missing

    if len(text_content) < 200: return []
    
    found_rules = agent.extract_rules_from_text(text_content, city_name)
    
    # Attach source text and page number to each rule
    results_with_source = []
    for rule in found_rules:
        results_with_source.append({
            "rule": rule,
            "source_text": text_content, # This will be the document content in Chroma
            "page_number": page_num
        })
    return results_with_source

# --- MAIN EXECUTION SCRIPT (Now with ChromaDB) ---
def run_extraction_pipeline(input_path: str, city_name: str):
    print(f"--- Starting HIGH-PERFORMANCE AI Curation for {city_name} ---")
    
    if not os.path.exists(input_path): raise FileNotFoundError(f"Input file not found: {input_path}.")
    with open(input_path, 'r', encoding='utf-8') as f: unstructured_data = json.load(f)

    agent = RuleExtractionAgent()
    all_extracted_items = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        results = list(tqdm(
            executor.map(lambda page: process_page(page, city_name, agent), unstructured_data),
            total=len(unstructured_data), desc=f"Processing pages for {city_name}"
        ))

    for page_results in results:
        if page_results: all_extracted_items.extend(page_results)
    
    print(f"\nAI extraction complete. Found {len(all_extracted_items)} potential rules.")

    # --- De-duplicate the results ---
    print("De-duplicating extracted rules...")
    unique_items = {}
    for item in all_extracted_items:
        rule = item["rule"]
        rule_id = rule.get("id")
        if rule_id and rule_id not in unique_items:
            unique_items[rule_id] = item
    
    final_items_to_commit = list(unique_items.values())
    print(f"Found {len(final_items_to_commit)} unique rules to process.")
    
    if not final_items_to_commit:
        print("No new rules to commit.")
        return

    # --- Initialize ChromaDB Client ---
    db_client = ChromaDBClient()
    total_rules_committed = 0
    
    print("Committing new unique rules to ChromaDB...")
    for item in tqdm(final_items_to_commit, desc="Saving to DB"):
        rule_data = item["rule"]
        source_text = item["source_text"]
        
        # Add to ChromaDB
        # We pass the full source text as the document content, AND the page number
        page_num = item.get("page_number", 0)
        success = db_client.add_rule(rule_data, document_content=source_text, page_number=page_num)
        if success:
            total_rules_committed += 1
    
    print(f"Commit successful. Added {total_rules_committed} new rules to ChromaDB.")
    print(f"\n--- Curation Complete for {city_name} ---")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract rules and load them into the database.")
    parser.add_argument("--input", required=True, help="Path to the OCR'd JSON file.")
    parser.add_argument("--city", required=True, help="The name of the city for these rules.")
    
    args = parser.parse_args()
    run_extraction_pipeline(args.input, args.city)


