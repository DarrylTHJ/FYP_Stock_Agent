import os
import chromadb
from chromadb.utils import embedding_functions
from google import genai
from dotenv import load_dotenv

# Load .env
load_dotenv()

# --- CONFIGURATION ---
DB_PATH = "./chroma_db"
COLLECTION_NAME = "financial_knowledge"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# --- API SETUP ---
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError("API Key not found! Check your .env file.")

client = genai.Client(api_key=api_key)

# --- CHROMA SETUP ---
chroma_client = chromadb.PersistentClient(path=DB_PATH)
ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL)
collection = chroma_client.get_collection(name=COLLECTION_NAME, embedding_function=ef)

def retrieve_filtered(query, source_type, n=5):
    """
    Retrieves context SPECIFICALLY for one source type.
    """
    print(f"  ...searching {source_type} data...")
    
    results = collection.query(
        query_texts=[query],
        n_results=n,
        where={"source_type": source_type} # <--- THE MAGIC FILTER
    )

    context_text = ""
    if results['documents']:
        docs = results['documents'][0]
        # We don't need to fetch metadata for source_type here since we know it!
        for doc in docs:
            context_text += f"- {doc}\n"
    
    return context_text if context_text else "No relevant data found."

def generate_comparison(query, retail_ctx, inst_ctx):
    """
    Asks Gemini to analyze both sides separately.
    """
    print("🤖 Analyzing differences...")
    
    prompt = f"""
    You are a Financial Analyst System. You have access to two distinct datasets.
    
    USER QUESTION: {query}
    
    DATASET 1: INSTITUTIONAL (Official Reports, Principles)
    {inst_ctx}
    
    DATASET 2: RETAIL (Social Sentiment, YouTube Opinions)
    {retail_ctx}
    
    INSTRUCTIONS:
    Please provide your response in the following strict format:
    
    ### 🏛️ Institutional Perspective
    (Summarize the findings from Dataset 1. Focus on facts, fundamentals, and risk.)
    
    ### 🗣️ Retail/Market Sentiment
    (Summarize the findings from Dataset 2. Focus on opinions, hype, and psychology.)
    
    ### ⚖️ Analysis of Divergence
    (Compare the two. Are they agreeing? Is the retail crowd ignoring a risk the institutions see? Or vice versa?)
    """

    try:
        response = client.models.generate_content(
            model='gemma-3-12b-it',
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"Error: {e}"

def main():
    print("==================================================")
    print("   Dual-Source Financial Analyst (FYP Agent)      ")
    print("==================================================")
    
    while True:
        user_input = input("\nEnter Query (or 'exit'): ")
        if user_input.lower() in ['exit', 'quit']:
            break
            
        # 1. Parallel Retrieval
        print("\n🔍 Retrieving data...")
        institutional_data = retrieve_filtered(user_input, "institutional")
        retail_data = retrieve_filtered(user_input, "retail")
        
        # 2. Check if we found ANYTHING
        if "No relevant data" in institutional_data and "No relevant data" in retail_data:
            print("❌ No data found in either category.")
            continue
            
        # 3. Generate Answer
        answer = generate_comparison(user_input, retail_data, institutional_data)
        
        print("\n" + answer + "\n")
        print("-" * 60)

if __name__ == "__main__":
    main()