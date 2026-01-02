import os
import json
import time
from google import genai
from google.api_core import exceptions
from dotenv import load_dotenv

# 1. Setup
load_dotenv()
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Use Gemma-3-27b-it (Consistent with your processor)
# --- THE MAGIC LIST ---
# We list models from "Best/Fastest" to "Backup".
# If the first one hits a limit, we go to the second.
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

# 2. Load the Knowledge Base (Your JSON file)
# IMPORTANT: Update this filename to match the JSON file you just created!
KNOWLEDGE_FILE = "data_raw/retail_ob2wq6VjmM0_processed.json"

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
        print(f"❌ Error: Knowledge file not found at {filepath}")
        return []

def ask_retail_agent(user_question):
    # Load logic
    knowledge_base = load_knowledge(KNOWLEDGE_FILE)
    if not knowledge_base:
        return

    # Prepare the "Brain Dump" string
    # We convert the JSON back into a string to feed the AI context
    knowledge_str = json.dumps(knowledge_base, indent=2)

    print(f"🔹 Retail Agent is thinking about: '{user_question}'...")

    # 3. The Persona Prompt (The Magic Sauce)
    prompt = f"""
    You are the "Retail Investor Agent". 
    Persona: You mimic 'Alfred Chen' (Malaysian financial educator).
    Tone: Casual, heuristic-driven, beginner-friendly, uses analogies.
    
    Your Knowledge Base (Facts & Principles extracted from your videos):
    {knowledge_str}
    
    INSTRUCTIONS:
    1. Answer the user's question using ONLY the Principles and Facts from your Knowledge Base above.
    2. If the answer isn't in the knowledge base, admit you don't know based on this specific video.
    3. Explain your reasoning clearly, citing the "Principles" found in the data.
    
    User Question: {user_question}
    """

    try:
       return generate_with_fallback(prompt)
    except Exception as e:
        return f"❌ Error: {e}"

    # try:
    #     response = model.generate_content(prompt)
        
    #     print("\n" + "="*40)
    #     print("🤖 RETAIL AGENT SAYS:")
    #     print("="*40)
    #     print(response.text)
    #     print("="*40)

    # except Exception as e:
    #     print(f"❌ Error: {e}")

if __name__ == "__main__":
    # Test Question related to the video content
    # (Since the video is "5 ways to grow snowball", we ask a relevant question)
    ask_retail_agent("How do I grow my capital if I have a small starting amount?")