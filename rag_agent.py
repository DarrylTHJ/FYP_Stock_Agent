import os
from dotenv import load_dotenv
import chromadb
from chromadb.utils import embedding_functions
from google import genai  # UPDATED IMPORT for new SDK

load_dotenv()

# --- CONFIGURATION ---
DB_PATH = "./chroma_db"
COLLECTION_NAME = "financial_knowledge"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# --- API SETUP (NEW SDK) ---
# Make sure your environment variable matches this name exactly
# If you are testing locally, you can hardcode it inside the string (but don't commit it!)
api_key = os.environ.get("GEMINI_API_KEY") 

if not api_key:
    raise ValueError("API Key not found! Please set GEMINI_API_KEY environment variable.")

# Initialize the Client (The new way)
client = genai.Client(api_key=api_key)

# --- CHROMA DB SETUP ---
print(f"Connecting to Vector DB at {DB_PATH}...")
chroma_client = chromadb.PersistentClient(path=DB_PATH)
ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL)
collection = chroma_client.get_collection(name=COLLECTION_NAME, embedding_function=ef)

def retrieve_context(query, n_results=5, source_filter=None):
    """
    Searches the Vector DB for the most relevant facts/opinions.
    """
    print(f"\n🔍 Searching database for: '{query}'...")
    
    where_clause = {"source_type": source_filter} if source_filter else None

    results = collection.query(
        query_texts=[query],
        n_results=n_results,
        where=where_clause
    )

    context_text = ""
    if results['documents']:
        docs = results['documents'][0]
        metas = results['metadatas'][0]

        for i, doc in enumerate(docs):
            source = metas[i].get('source_type', 'Unknown').upper()
            category = metas[i].get('category', 'General').upper()
            context_text += f"- [{source} | {category}] {doc}\n"
    
    return context_text

def query_llm(user_question, context):
    """
    Sends the Context + Question to Gemini using the NEW SDK.
    """
    print("🤖 Thinking...")
    
    prompt = f"""
    You are an expert Financial Analyst AI. Answer the user's question using ONLY the provided context.
    
    DATA SOURCES:
    - RETAIL: YouTube Transcripts (Opinions/Facts)
    - INSTITUTIONAL: PDF Reports (Facts/Principles)

    INSTRUCTIONS:
    1. Synthesize the context.
    2. Mention if info is 'Retail' or 'Institutional'.
    3. If the answer isn't in the context, state that clearly.

    --- CONTEXT ---
    {context}
    --- END CONTEXT ---

    USER QUESTION: {user_question}
    """

    # UPDATED: The new generation syntax
    try:
        response = client.models.generate_content(
            model='gemma-3-12b-it', # Or 'gemini-1.5-flash'
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"Error connecting to Gemini: {e}"

def main():
    print("==========================================")
    print("   Financial Analyst Agent (RAG System)   ")
    print("==========================================")
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ")
        if user_input.lower() in ['exit', 'quit']:
            break
            
        # 1. RETRIEVE
        context = retrieve_context(user_input)
        
        # 2. CHECK CONTEXT
        if not context:
            print("Agent: I couldn't find any relevant data in the database.")
            continue
            
        # 3. GENERATE
        answer = query_llm(user_input, context)
        
        # 4. DISPLAY
        print(f"\nAgent:\n{answer}\n")
        print("-" * 50)

if __name__ == "__main__":
    main()