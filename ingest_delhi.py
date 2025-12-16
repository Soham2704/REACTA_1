from ingest_pdf import ingest_pdf

if __name__ == "__main__":
    pdf_path = "io/Delhi_Master_Plan.pdf"
    city_name = "Delhi"
    output_json = "io/delhi_content.json"
    
    print("--- Triggering Delhi Ingestion (Local) ---")
    ingest_pdf(pdf_path, city_name, output_json)
