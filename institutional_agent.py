import os
import json
import time
from google import genai
from google.api_core import exceptions
from dotenv import load_dotenv


load_dotenv()
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
MODEL_ROSTER = [
    "gemini-2.5-flash-lite",
    "gemini-2.5-flash",   # Tier 2: Experimental, often has separate quota.
    "gemini-3-flash",         # Tier 3: The one you were using.
    "gemma-3-27b",         # Tier 4: Slower, but smarter backup.
    "gemma-3-12b", 
    "gemma-3-1b", 
    "gemma-3-2b", 
    "gemma-3-3b", 
]

# Load the Institutional Knowledge
KNOWLEDGE_FILE = "data_raw/Banking_20260102_HLIB_processed.json"

def generate_with_fallback(prompt):
    """
    Cycles through models if a Quota Error (429) occurs.
    """
    for model_name in MODEL_ROSTER:
        try:
            print(f"🔄 Trying model: {model_name}...")
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            return response.text  # If successful, return and exit loop
            
        except exceptions.ResourceExhausted:
            print(f"⚠️ Quota hit for {model_name}. Switching to next model...")
            continue  # Try the next model in the list
            
        except Exception as e:
            # If it's a non-quota error (like internet down), print it but keep trying
            print(f"❌ Error with {model_name}: {e}")
            continue

    return "❌ All models are currently busy or out of quota. Please wait 60 seconds."

def load_knowledge(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def ask_institutional_agent(user_question):
    knowledge_base = load_knowledge(KNOWLEDGE_FILE)
    if not knowledge_base:
        print("❌ Error: No knowledge found.")
        return

    knowledge_str = json.dumps(knowledge_base, indent=2)

    print(f"🔹 Institutional Agent is analysing: '{user_question}'...")

    # PERSONA: Professional, Formal, HLIB Analyst
    prompt = f"""
    You are the "Institutional Agent" (Modelled after HLIB Research).
    Tone: Professional, objective, formal, data-driven. Use terms like 'We project', 'Valuation', 'Upside'.
    
    Your Knowledge Base (Extracted from HLIB Report):
    {knowledge_str}
    
    INSTRUCTIONS:
    1. Answer the question using ONLY the data above.
    2. Focus on "Facts" (Numbers) and "Opinions" (Target Prices/Calls).
    3. If data is missing, state: "The report does not provide sufficient data on this metric."
    
    User Question: {user_question}
    """
    try:
        return generate_with_fallback(prompt)
    except Exception as e:
        return f"❌ Error: {e}"

    # try:
    #     response = model.generate_content(prompt)
    #     print("\n" + "="*40)
    #     print("🏛️ INSTITUTIONAL AGENT SAYS:")
    #     print("="*40)
    #     print(response.text)
    #     print("="*40)

    # except Exception as e:
    #     print(f"❌ Error: {e}")

if __name__ == "__main__":
    # Test Question (Standard for reports)
    ask_institutional_agent("What is the target price and the recommendation for this stock?")