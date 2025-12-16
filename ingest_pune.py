from ingest_pdf import ingest_pdf

if __name__ == "__main__":
    pdf_path = "io/Pune_DCPR_2018.pdf"
    city_name = "Pune"
    output_json = "io/pune_content.json"
    
    print("--- Triggering Pune Ingestion ---")
    ingest_pdf(pdf_path, city_name, output_json)
