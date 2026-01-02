import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Use Gemma-3-27b-it
model = genai.GenerativeModel('gemma-3-27b-it')

# IMPORTANT: Ensure this matches the text file you generated from the PDF earlier
INPUT_FILE = "data_raw\Banking_20260102_HLIB.txt"

def process_institutional_data(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            raw_text = f.read()
    except FileNotFoundError:
        print(f"❌ Error: Could not find {filepath}. Did you run the PDF scraper?")
        return

    print(f"🔹 Processing Institutional Report ({len(raw_text)} chars)...")

    # Prompt adapted for Institutional Reports
    prompt = f"""
    You are a Financial Analyst Data Extractor.
    
    Task: Extract logical units from this Equity Research Report.
    
    Output: A valid JSON list only.
    
    Schema:
    {{
        "text": "Exact quote from report",
        "type": "FACT" (e.g., Earnings, Revenue, Margins) OR "PRINCIPLE" (e.g., Valuation method, Industry trend) OR "OPINION" (e.g., Buy call, Target Price),
        "reasoning": "Context for this classification"
    }}

    REPORT TEXT:
    {raw_text[:35000]}
    """

    try:
        response = model.generate_content(prompt)
        
        # Clean JSON
        clean_text = response.text.strip()
        if clean_text.startswith("```json"): clean_text = clean_text[7:]
        if clean_text.startswith("```"): clean_text = clean_text[3:]
        if clean_text.endswith("```"): clean_text = clean_text[:-3]

        data = json.loads(clean_text)

        output_filename = filepath.replace(".txt", "_processed.json")
        with open(output_filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

        print(f"✅ Success! Institutional JSON saved to: {output_filename}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    process_institutional_data(INPUT_FILE)