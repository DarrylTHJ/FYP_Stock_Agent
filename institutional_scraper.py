import os
import pdfplumber

# Configuration
# Put your downloaded PDFs in this folder
SOURCE_PDF_DIR = "data/institutional/raw" 
# The script will save the text files here
OUTPUT_TXT_DIR = "data/institutional/scraped" 

def batch_convert_local_pdfs():
    # 1. Create output folder if it doesn't exist
    os.makedirs(OUTPUT_TXT_DIR, exist_ok=True)
    
    # 2. Check if source folder exists
    if not os.path.exists(SOURCE_PDF_DIR):
        print(f"❌ Error: Folder '{SOURCE_PDF_DIR}' not found.")
        print("   Please create it and put your PDF files inside.")
        return

    # 3. List all PDF files
    pdf_files = [f for f in os.listdir(SOURCE_PDF_DIR) if f.lower().endswith(".pdf")]
    
    if not pdf_files:
        print(f"⚠️ No PDF files found in '{SOURCE_PDF_DIR}'.")
        return

    print(f"📋 Found {len(pdf_files)} PDFs. Starting extraction...")

    for i, filename in enumerate(pdf_files):
        pdf_path = os.path.join(SOURCE_PDF_DIR, filename)
        
        # Define output filename (e.g., "institutional_hlib_maybank.txt")
        # We add a prefix so we know it's institutional data later
        txt_filename = f"institutional_{filename.replace('.pdf', '.txt')}"
        txt_path = os.path.join(OUTPUT_TXT_DIR, txt_filename)

        # Check for duplicates (Idempotency)
        if os.path.exists(txt_path):
            print(f"⏭️  [{i+1}/{len(pdf_files)}] Skipping {filename} (Already extracted)")
            continue

        print(f"📖 [{i+1}/{len(pdf_files)}] Extracting: {filename}...")

        try:
            full_text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        full_text += text + "\n"
            
            # Save the text
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(full_text)
                
            print(f"   ✅ Saved to {txt_filename}")

        except Exception as e:
            print(f"   ❌ Failed to read {filename}: {e}")

    print("\n🎉 Batch extraction complete!")

if __name__ == "__main__":
    batch_convert_local_pdfs()