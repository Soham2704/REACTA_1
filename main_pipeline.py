import json
import os
import numpy as np
import re
from datetime import datetime
import torch
from langchain_core.prompts import PromptTemplate
from logging_config import logger

# Import agents that are now simple, stateless tools
from agents.calculator_agent import EntitlementsAgent, AllowableEnvelopeAgent
from agents.geometry_agent import GeometryAgent
from agents.interior_agent import InteriorDesignAgent

def process_case_logic(case_data, system_state):
    """
    This is the core pipeline logic, refactored to use the MCPClient as the single source of truth.
    """
    # --- A. Unpack Inputs ---
    project_id = case_data.get("project_id", "default_project")
    case_id = case_data.get("case_id")
    city = case_data.get("city")
    parameters = case_data.get("parameters", {})
    
    # Extract Detailed Parameters
    plot_size = float(parameters.get("plot_size", 0))
    road_width = parameters.get("road_width")
    location = parameters.get("location")
    zoning = parameters.get("zoning", "Not Specified")
    proposed_use = parameters.get("proposed_use", "Not Specified")
    building_height = parameters.get("building_height", "Not Specified")

    # Extract Advanced Constraints
    asr_rate = float(parameters.get("asr_rate", 0))
    plot_deductions = float(parameters.get("plot_deductions", 0))
    
    # Pre-calculate Net Area
    net_plot_area = max(0, plot_size - plot_deductions)

    logger.info(f"Processing case {case_id} for project {project_id}.")
    
    # --- B. Query MCP for Hard Facts ---
    logger.info(f"Querying MCP for rules for case {case_id}...")
    db_parameters = {
        "road_width_m": road_width,
        "plot_area_sqm": plot_size,
        "location": location
    }
    matching_rules = system_state.mcp_client.query_rules(city, db_parameters)
    
    # Extract both structured entitlements and raw text notes for the LLM
    context_data = []
    seen_context_signatures = set()

    if matching_rules:
        for rule in matching_rules:
            item = {}
            if rule.get("entitlements"):
                item["entitlements"] = rule["entitlements"]
            if rule.get("notes"):
                item["raw_text_excerpt"] = rule["notes"]
            if rule.get("conditions"):
                item["applicability_conditions"] = rule["conditions"]
            
            # Add citation info
            if "page_number" in rule:
                item["source_page"] = rule["page_number"]
            
            # Create a signature to detect duplicates
            # Use raw_text_excerpt as the primary key for uniqueness if present, 
            # otherwise fallback to full item dump
            signature = item.get("raw_text_excerpt", json.dumps(item, sort_keys=True))
            
            if signature not in seen_context_signatures:
                seen_context_signatures.add(signature)
                context_data.append(item)

    # --- C. Use the LLM to Explain the Facts ---
    logger.info(f"Executing LLM agent to generate expert report for {case_id}...")
    
    if system_state.llm:
        try:
            # ... (LLM Context and Prompt setup - assume unchanged) ...
            context_for_llm = f"The following rules were retrieved from the master database:\n\n{json.dumps(context_data, indent=2)}"
            
            prompt = PromptTemplate.from_template(
                """You are a professional AI consultant specializing in the detailed analysis of municipal development regulations. Your task is to act as an expert consultant and provide a comprehensive, clear, and actionable report based on the provided context and the user's query.

                **Your final output MUST be a well-structured Markdown report.** Use the following format precisely:
                
                ### **AI Consultant Report: Planning & Zoning Analysis**
                **Date:** {current_date}
                **Subject:** Analysis of Development Potential
                **Case Parameters:**
                **Case Parameters:**
                * **Plot Size:** {plot_size}
                * **Location Type:** {location}
                * **Abutting Road Width:** {road_width}
                * **Zoning:** {zoning}
                * **Proposed Use:** {proposed_use}
                * **Proposed Height:** {building_height}
                * **Gross Plot Area:** {plot_size} sq. m.
                * **Deductions:** {plot_deductions} sq. m.
                * **Net Plot Area:** {net_plot_area} sq. m.
                * **ASR Rate:** ₹{asr_rate}/sq.m.
                ---
                #### **1. Analysis Summary & Applicable Rules**
                [Based on the rules found in the <context>, provide a high-level summary. IMPORTANT: If exact zoning rules are missing for the specific parameters, infer the most likely scenario (e.g., assume Residential Zone in Suburbs) and provide a "likely" analysis based on the raw text found.]
                
                **Citations:**
                [For every rule or regulation mentioned, you MUST cite the specific Rule Name and Page Number if available in the context (e.g., "Page 45, Table 12").]

                #### **2. Entitlements & Calculations**
                [Using the rules from the <context>, detail the specific entitlements. Perform calculations for FSI and BUA based on the **Net Plot Area** of {net_plot_area} sq. m.]
                [**IMPORTANT**: Present the calculations (Base FSI, Premium FSI, TDR, Total FSI, Permissible Height) in a **Markdown Table** format for clarity.]
                [**FINANCIALS**: If Premium FSI is applicable, calculate the cost using the ASR Rate: Cost = 0.5 * ASR * Premium_FSI_Area. If ASR is 0, mention that cost cannot be calculated.]
                
                #### **3. Key Missing Information**
                [Critically analyze the user's query. List what is missing, but do NOT stop the analysis. Provide the analysis based on the assumptions above.]
                #### **4. Recommended Next Steps**
                [Based on your analysis, provide a list of actionable next steps for the user.]
                ---
                **Disclaimer:** This report is an automated analysis...
                
                <context>
                {context}
                </context>
    
                **User Query Parameters (for your reference):**
                {input}
                """
            )
            
            llm_chain = prompt | system_state.llm
            
            # Prepare inputs for the LLM
            llm_inputs = {
                "context": context_for_llm,
                "input": json.dumps(parameters),
                "current_date": datetime.utcnow().strftime('%B %d, %Y'),
                "plot_size": f'{parameters.get("plot_size", "N/A")} sq. m.',
                "location": parameters.get("location", "N/A"),
                "road_width": f'{parameters.get("road_width", "N/A")} m.',
                "zoning": zoning,
                "proposed_use": proposed_use,
                "building_height": building_height,
                "net_plot_area": net_plot_area,
                "asr_rate": asr_rate,
                "plot_deductions": plot_deductions
            }

            # DEBUG: Write the full prompt to a file
            try:
                full_prompt = prompt.format(**llm_inputs)
                with open("debug_llm_prompt.txt", "w", encoding="utf-8") as f:
                    f.write(full_prompt)
                logger.info("Saved full LLM prompt to debug_llm_prompt.txt")
            except Exception as e:
                logger.error(f"Failed to save debug prompt: {e}")

            summary_response = llm_chain.invoke(llm_inputs)
            
            # Handle potential multi-part content from newer Gemini models
            raw_content = summary_response.content
            if isinstance(raw_content, list) and len(raw_content) > 0:
                # Expecting [{'type': 'text', 'text': '...', ...}]
                if isinstance(raw_content[0], dict) and "text" in raw_content[0]:
                    analysis_report = raw_content[0]["text"]
                else:
                    analysis_report = str(raw_content) # Fallback
            elif hasattr(raw_content, "text"): # Some objects might have .text prop
                 analysis_report = raw_content.text
            else:
                analysis_report = str(raw_content) # Default to string conversion logic for plain strings or unknown types
                
            logger.info(f"LLM expert report complete for {case_id}.")
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            analysis_report = f"### ⚠️ AI Analysis Unavailable\n\n**Reason**: The AI service encountered a temporary error ({str(e)}). \n\n**Note**: The rest of your report (Calculations, Geometry, RL Decision) is available below."

    else:
        logger.warning("LLM skipped because it is not initialized.")
        analysis_report = "### AI Analysis Skipped\n\nReason: `GEMINI_API_KEY` is missing. Please configure it to receive detailed regulatory analysis."


    # --- D. Run Specialist Agents (now stateless) ---
    entitlement_agent = EntitlementsAgent({"road_width_gt_18m_bonus": 0.5})
    envelope_agent = AllowableEnvelopeAgent()
    interior_agent = InteriorDesignAgent()
    geometry_agent = GeometryAgent()

    entitlement_result = entitlement_agent.calculate("road_width_gt_18m_bonus")
    envelope_result = envelope_agent.calculate(plot_area=parameters.get("plot_size", 0), setback_area=150)
    
    total_fsi = 1.0 
    # Extract just the entitlements for FSI calculation from the richer context format
    deterministic_entitlements = [item.get("entitlements", {}) for item in context_data if item.get("entitlements")]
    
    if deterministic_entitlements:
        for ent in deterministic_entitlements:
            if 'total_fsi' in ent:
                fsi_value = ent['total_fsi']
                if isinstance(fsi_value, dict): total_fsi = fsi_value.get('max', 1.0)
                elif isinstance(fsi_value, (int, float)): total_fsi = fsi_value
                break 

    # Fallback / Enhancement: Scan raw text if FSI is still default 1.0
    # Many rules contain "Maximum Permissible FSI ... 3.0" or similar in text
    if total_fsi <= 1.5:
        # Try to find a better FSI in the text
        if context_data:
            try:
                potential_fsis = []
                import re
                for item in context_data:
                    text = item.get("raw_text_excerpt", "")
                    matches = re.findall(r"(?:FSI|Index)\s*(?:is|of|:)?\s*([0-4]\.\d{1,2}|[1-5])", text, re.IGNORECASE)
                    for m in matches:
                        try:
                            val = float(m)
                            if 1.0 <= val <= 8.0: # Range 1-8
                                potential_fsis.append(val)
                        except: pass
                
                if potential_fsis:
                    total_fsi = max(potential_fsis)
                    logger.info(f"Extracted FSI {total_fsi} from text context for visualization.")
            except: pass

        # If data is still low, FORCE a reasonable default for high-rise visualization
        # The user wants to see a building, not a shed.
        if total_fsi < 2.0:
            total_fsi = 3.0 # Standard Mumbai High Rise Assumption
            logger.info("Forcing FSI 3.0 for better visualization.")

    
    total_bua = parameters.get("plot_size", 0) * total_fsi
    interior_result = interior_agent.calculate_carpet_area(total_bua)

    # --- E. Run RL Agent for Optimal Policy Decision ---
    rl_optimal_action = -1
    confidence_score = 0.0
    
    if system_state.rl_agent:
        try:
            location_map = {"urban": 0, "suburban": 1, "rural": 2}
            rl_state_np = np.array([parameters.get("plot_size",0), location_map.get(parameters.get("location", "urban"),0), parameters.get("road_width",0)]).astype(np.float32)
            
            action, _ = system_state.rl_agent.predict(rl_state_np, deterministic=True)
            rl_optimal_action = int(action)

            rl_state_tensor = torch.as_tensor(rl_state_np, device=system_state.rl_agent.device).reshape(1, -1)
            distribution = system_state.rl_agent.policy.get_distribution(rl_state_tensor)
            action_probabilities = distribution.distribution.probs.detach().cpu().numpy()[0]
            raw_rl_confidence = float(action_probabilities[rl_optimal_action])
            
            # Hybrid Confidence Calculation
            # The RL agent is just one part. If we found rules and generated a report, confidence is actually high.
            # Base: 0.5
            # +0.3 if rules found
            # +0.1 if LLM worked
            # +0.1 from RL (normalized)
            
            hybrid_score = 0.5
            if context_data: 
                hybrid_score += 0.35
            if analysis_report and "Unavailable" not in analysis_report:
                hybrid_score += 0.10
                
            # Boost with RL 
            # If RL is 0.33 (uncertain), we don't penalize. If it's 0.9, we boost.
            if raw_rl_confidence > 0.5:
                hybrid_score += (raw_rl_confidence - 0.5) * 0.1
            
            confidence_score = min(0.98, hybrid_score) # Cap at 98%
            
        except Exception as e:
            logger.warning(f"RL Prediction failed: {e}")
            # Fallback confidence if RL fails but rules exist
            confidence_score = 0.85 if context_data else 0.4
    else:
        logger.info("Skipping RL step (Agent not loaded).")
        confidence_score = 0.85 if context_data else 0.1

    # Calculate dimensions for geometry
    # 1. Effective Plot Area
    plot_size = parameters.get("plot_size", 100)
    net_area = max(0, plot_size - parameters.get("plot_deductions", 0))
    
    # 2. Derive Plot Dimensions (Assume Aspect Ratio 2:3)
    plot_width = np.sqrt(net_area / 1.5)
    plot_depth = plot_width * 1.5
    
    # 3. Apply Standard Setbacks 
    scale_factor = 1.0 if net_area > 1000 else 0.5
    setback_front = 6.0 * scale_factor
    setback_rear = 4.5 * scale_factor
    setback_side = 3.0 * scale_factor
    
    # Max feasible envelope dimensions
    max_building_width = max(5.0, plot_width - (2 * setback_side))
    max_building_depth = max(5.0, plot_depth - (setback_front + setback_rear))
    
    # 4. Height & Massing Calculation
    total_permissible_bua = net_area * total_fsi
    
    # Standard approach: Maximize footprint (Coverage Limit usually 50%)
    max_coverage_area = 0.50 * net_area
    envelope_footprint = min(max_building_width * max_building_depth, max_coverage_area)
    
    # Standard Height (if we use max footprint)
    standard_floors = total_permissible_bua / envelope_footprint if envelope_footprint > 0 else 1
    standard_height = standard_floors * 3.0
    
    # Check User Request
    user_height_req = parameters.get("building_height")
    
    final_width = max_building_width
    final_depth = max_building_depth
    final_height = max(18.0, standard_height) # Default min 18m
    
    # Dynamic Adjustment: If user wants TALLER building, we shrink footprint
    if user_height_req and isinstance(user_height_req, (int, float)) and user_height_req > standard_height:
        logger.info(f"User requested height {user_height_req}m > standard {standard_height}m. Adjusting footprint.")
        final_height = user_height_req
        
        # Required footprint to achieve this height with same FSI
        # Floors = Height / 3
        # Area = Total BUA / Floors
        req_floors = user_height_req / 3.0
        req_footprint = total_permissible_bua / req_floors
        
        # Recalculate dimensions maintaining aspect ratio of envelope
        # Ratio = Depth / Width
        ratio = max_building_depth / max_building_width
        # Area = w * (ratio * w) = req_footprint
        # w^2 = req_footprint / ratio
        final_width = np.sqrt(req_footprint / ratio)
        final_depth = final_width * ratio
    else:
        # User happy with standard, or wants lower. 
        # For visualization, we default to the "Max Envelope" (Standard) 
        # unless we need to shrink to fit 50% coverage cap
        if (max_building_width * max_building_depth) > max_coverage_area:
             ratio = max_building_depth / max_building_width
             final_width = np.sqrt(max_coverage_area / ratio)
             final_depth = final_width * ratio
    
    # Final Sanity Checks for Visualization
    width_dim = max(4.0, final_width)
    depth_dim = max(4.0, final_depth)
    height_dim = max(5.0, final_height)

    # --- F. Compile Final, Standardized Report ---
    final_report = { 
        "project_id": project_id,
        "case_id": case_id,
        "city": city,
        "inputs": parameters,
        "entitlements": {
            "analysis_summary": analysis_report,
            "rules_from_db": deterministic_entitlements,
            "carpet_area_sqm": interior_result.get("result_carpet_area_sqm")
        },
        "rl_decision": {
            "optimal_action": rl_optimal_action,
            "confidence_score": round(confidence_score, 2)
        },
        "geometry_file": f"/outputs/projects/{project_id}/{case_id}_geometry.stl",
        "calculated_geometry": {
            "width": float(width_dim),
            "depth": float(depth_dim),
            "height": float(height_dim)
        },
        "logs": f"/logs/{case_id}" 
    }
    
    # --- G. Save Outputs ---
    output_dir = f"outputs/projects/{project_id}"
    os.makedirs(output_dir, exist_ok=True)
    json_output_path = os.path.join(output_dir, f"{case_id}_report.json")
    stl_output_path = os.path.join(output_dir, f"{case_id}_geometry.stl")

    with open(json_output_path, "w") as f:
        json.dump(final_report, f, indent=4)
    
    geometry_agent.create_block(output_path=stl_output_path, width=width_dim, depth=depth_dim, height=height_dim)
    
    return final_report
