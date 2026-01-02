import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

print("🔍 Fetching available models...\n")

try:
    # Just list everything. We won't filter by property to avoid AttributeErrors.
    for model in client.models.list():
        print(f"✅ {model.name}")
        # If you want to see what other attributes exist, uncomment below:
        # print(dir(model)) 
            
except Exception as e:
    print(f"❌ Error listing models: {e}")