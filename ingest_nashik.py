from ingest_pdf import ingest_pdf

if __name__ == "__main__":
    pdf_path = "io/Nashik_DCPR.pdf"
    city_name = "Nashik"
    output_json = "io/nashik_content.json"
    
    print("--- Triggering Nashik Ingestion (Local) ---")
    ingest_pdf(pdf_path, city_name, output_json)
