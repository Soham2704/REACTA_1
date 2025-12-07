import fitz  # PyMuPDF
import json
import os
import argparse
from tqdm import tqdm
from extract_rules_ai import run_extraction_pipeline
import pytesseract
from PIL import Image
import io

def ingest_pdf(pdf_path, city_name, output_json_path):
    """
    Reads a PDF, extracts text from each page using Tesseract OCR, 
    saves as JSON, and triggers the AI extraction pipeline.
    """
    print(f"--- Starting Ingestion for {pdf_path} ---")
    
    if not os.path.exists(pdf_path):
        print(f"Error: PDF not found at {pdf_path}")
        return

    # Robustly find Tesseract
    tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    if os.path.exists(tesseract_path):
        pytesseract.pytesseract.tesseract_cmd = tesseract_path
    else:
        # Check standard 32-bit path just in case
        tesseract_path_x86 = r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'
        if os.path.exists(tesseract_path_x86):
            pytesseract.pytesseract.tesseract_cmd = tesseract_path_x86
        else:
             print("[WARNING] Tesseract executable not found in standard paths. Assuming it is in PATH.")

    # 1. Extract Text (via Tesseract OCR)
    print("Extracting text from PDF pages using Tesseract OCR...")
    doc = fitz.open(pdf_path)
    pages_data = []
    
    for i, page in enumerate(tqdm(doc, desc="OCR Processing")):
        # Render page to an image (zoom=2 for better quality)
        zoom = 2 
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        
        # Convert to PIL Image
        img_data = pix.tobytes("png")
        image = Image.open(io.BytesIO(img_data))
        
        # Perform OCR
        try:
            text = pytesseract.image_to_string(image)
        except Exception as e:
            print(f"OCR Error on page {i}: {e}")
            text = "" # fallback
        
        # Store page number and content
        pages_data.append({
            "page": i + 1,
            "content": text
        })
    
    print(f"Extracted text from {len(pages_data)} pages.")
    
    # 2. Save Intermediate JSON
    print(f"Saving intermediate text data to {output_json_path}...")
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(pages_data, f, indent=4)
        
    # 3. Monitor API Key State
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key or "YOUR_KEY" in api_key:
        print("\n[WARNING] Valid GEMINI_API_KEY not found. AI extraction will likely fail or produce no rules.")
        print("Please ensure your .env file has a valid key.")
        # We proceed anyway, as the user might want to test the flow, 
        # but the extraction agent will probably return empty results or error out.
    
    # 4. Trigger AI Extraction
    print("\n--- Triggering AI Rule Extraction Agent ---")
    try:
        run_extraction_pipeline(output_json_path, city_name)
        print("\n--- Ingestion Complete ---")
    except Exception as e:
        print(f"\n[ERROR] Extraction pipeline failed: {e}")

if __name__ == "__main__":
    # Default configuration for the Hackathon/Demo
    DEFAULT_PDF = "io/DCPR_2034.pdf"
    DEFAULT_JSON = "temp_dcr_content.json"
    CITY = "Mumbai"
    
    ingest_pdf(DEFAULT_PDF, CITY, DEFAULT_JSON)
