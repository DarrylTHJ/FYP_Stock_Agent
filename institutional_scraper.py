import pdfplumber

# Target PDF file in your data_raw folder
PDF_PATH = "data_raw/Banking_20260102_HLIB.pdf"

def extract_text_from_pdf(pdf_path):
    full_text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            # Loop through every page
            for page in pdf.pages:
                # Extract text
                text = page.extract_text()
                if text:
                    full_text += text + "\n"


        
        # Save the raw text
        output_filename = pdf_path.replace(".pdf", ".txt")
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(full_text)
            
        print(f"✅ Success! PDF text extracted to {output_filename}")
        print("Preview of text (first 200 chars):")
        print(full_text[:200])

    except Exception as e:
        print(f"❌ Error reading PDF: {e}")

if __name__ == "__main__":
    extract_text_from_pdf(PDF_PATH)