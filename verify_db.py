import chromadb
from chromadb.utils import embedding_functions

# --- CONFIGURATION ---
DB_PATH = "./chroma_db"
COLLECTION_NAME = "financial_knowledge"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

def main():
    print(f"Connecting to ChromaDB at {DB_PATH}...")
    
    # 1. Connect to the Database
    client = chromadb.PersistentClient(path=DB_PATH)
    
    # 2. Get the Collection
    # Important: We must use the SAME embedding function as we did during ingestion
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL_NAME)
    
    try:
        collection = client.get_collection(name=COLLECTION_NAME, embedding_function=ef)
        count = collection.count()
        print(f"Success! Found collection '{COLLECTION_NAME}' with {count} documents.")
    except Exception as e:
        print(f"Error: Could not find collection. Did you run the ingestion script? \n{e}")
        return

    # 3. Test Query
    query_text = "What is the outlook for inflation and interest rates?"
    
    print(f"\n--- Running Test Query: '{query_text}' ---")
    
    results = collection.query(
        query_texts=[query_text],
        n_results=3, # Return top 3 matches
        # Optional: Filter by metadata (e.g., only search Institutional reports)
        # where={"source_type": "institutional"} 
    )

    # 4. Display Results
    for i in range(len(results['documents'][0])):
        doc = results['documents'][0][i]
        meta = results['metadatas'][0][i]
        dist = results['distances'][0][i]
        
        print(f"\nResult {i+1}:")
        print(f"  Source: {meta.get('source_type', 'Unknown')} ({meta.get('filename', '')})")
        print(f"  Category: {meta.get('category', 'Unknown')}")
        print(f"  Text: {doc[:150]}...") # Print first 150 chars
        print(f"  Distance: {dist:.4f}")

if __name__ == "__main__":
    main()