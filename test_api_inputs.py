import requests
import json

url = "http://localhost:8000/run_case"
payload = {
    "project_id": "debug_test",
    "case_id": "debug_case_dynamic_001",
    "city": "Mumbai",
    "document": "io/DCPR_2034.pdf",
    "parameters": {
        "plot_size": 5000,
        "location": "Island City",
        "road_width": 30.0,
        "zoning": "Residential",
        "proposed_use": "Residential",
        "building_height": 100.0,
        "asr_rate": 100,
        "plot_deductions": 0
    }
}

try:
    print(f"Sending payload: {json.dumps(payload, indent=2)}")
    response = requests.post(url, json=payload)
    response.raise_for_status()
    data = response.json()
    
    calc_geom = data.get("calculated_geometry", {})
    print("\n--- Response Geometry ---")
    print(json.dumps(calc_geom, indent=2))
    
    expected_width = 5000**0.5 # ~70.71
    if abs(calc_geom.get("width", 0) - expected_width) < 0.1:
        print("\n✅ API Validation Passed: Backend is respecting inputs.")
    else:
        print(f"\n❌ API Validation Failed: Expected width ~{expected_width}, got {calc_geom.get('width')}")

except Exception as e:
    print(f"\n❌ Request Failed: {e}")
    if 'response' in locals():
        print(response.text)
