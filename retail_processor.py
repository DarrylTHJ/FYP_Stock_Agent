import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

# 1. Setup
load_dotenv() 
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# USE THIS MODEL: Gemma 3 27b (Instruction Tuned)
# Note: If this specific string fails, try 'models/gemma-3-27b-it'
model = genai.GenerativeModel('gemma-3-27b-it')

# 2. File Selection (Make sure this matches your actual file)
INPUT_FILE = "data_raw/retail_ob2wq6VjmM0.txt" 

def process_transcript_with_gemma(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            raw_text = f.read()
    except FileNotFoundError:
        print(f"❌ Error: Could not find file {filepath}")
        return

    print(f"🔹 Read {len(raw_text)} characters. Sending to Gemma-3-27b...")

    # 3. The Prompt
    # We are very specific about JSON format here to stop Gemma from chatting.
    prompt = f"""
    You are a strictly logical data processor for a financial AI agent.
    
    Task: Analyze the provided transcript. Extract key logical units.
    
    Output Format: 
    Return ONLY a raw JSON list. No markdown formatting, no introduction, no "Here is your JSON".
    
    JSON Schema for each item:
    {{
        "text": "The exact sentence from the transcript",
        "type": "FACT" (if objective data) OR "PRINCIPLE" (if general rule) OR "OPINION" (if subjective view),
        "reasoning": "Brief explanation of your classification"
    }}

    TRANSCRIPT:
    {raw_text[:30000]} 
    """

    try:
        response = model.generate_content(prompt)
        
        # Clean up response (Gemma sometimes adds ```json ... ``` wrappers)
        clean_text = response.text.strip()
        if clean_text.startswith("```json"):
            clean_text = clean_text[7:]
        if clean_text.startswith("```"):
            clean_text = clean_text[3:]
        if clean_text.endswith("```"):
            clean_text = clean_text[:-3]
            
        # Parse JSON
        data = json.loads(clean_text)

        # 4. Save the result
        output_filename = filepath.replace(".txt", "_processed.json")
        with open(output_filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

        print(f"✅ Success! Processed data saved to: {output_filename}")
        print(f"   - Extracted {len(data)} logical units.")

    except json.JSONDecodeError:
        print("❌ Error: Gemma returned invalid JSON. It might have added extra text.")
        print("Raw output start:", response.text[:500]) # Print first 500 chars to debug
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    process_transcript_with_gemma(INPUT_FILE)