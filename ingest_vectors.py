import os
import json
import chromadb
from chromadb.utils import embedding_functions
import uuid

# --- CONFIGURATION ---
DB_PATH = "./chroma_db"
COLLECTION_NAME = "financial_knowledge"
DATA_DIRS = {
    "retail": "./data/retail/processed",
    "institutional": "./data/institutional/processed"
}
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

def load_processed_data(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

def main():
    # 1. Initialize ChromaDB
    print(f"Initializing ChromaDB at {DB_PATH}...")
    client = chromadb.PersistentClient(path=DB_PATH)
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL_NAME)
    
    # 2. Reset Collection (Optional: helps avoid duplicates while debugging)
    # Uncomment the next line if you want to start fresh every time
    # client.delete_collection(COLLECTION_NAME) 

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=ef
    )
    print(f"Connected to collection: {COLLECTION_NAME}")

    # 3. Processing Variables
    documents = []
    metadatas = []
    ids = []
    BATCH_SIZE = 100 
    total_inserted = 0

    for source_type, directory in DATA_DIRS.items():
        if not os.path.exists(directory):
            print(f"Skipping {directory} (not found)")
            continue

        print(f"Processing source: {source_type}...")
        
        for filename in os.listdir(directory):
            if not filename.endswith(".json"):
                continue

            file_path = os.path.join(directory, filename)
            json_content = load_processed_data(file_path)
            
            if not json_content: 
                continue

            # --- UPDATED PARSING LOGIC ---
            # Extract the list from the "data" key
            items = json_content.get("data", [])
            
            if not isinstance(items, list):
                print(f"Warning: 'data' is not a list in {filename}")
                continue

            for item in items:
                # Extract text and type safely
                text_content = item.get("text", "")
                category_type = item.get("type", "UNKNOWN")
                
                # Validation: Skip empty strings or very short noise
                if not text_content or len(text_content) < 5:
                    continue

                documents.append(text_content)
                
                # Metadata: Store the 'type' (PRINCIPLE, FACT, etc.) here
                metadatas.append({
                    "source_type": source_type,
                    "filename": filename,
                    "category": category_type, 
                    "origin_source": filename.replace(".json", "")
                })
                
                ids.append(f"{filename}-{uuid.uuid4()}")

                # Batch Upsert
                if len(documents) >= BATCH_SIZE:
                    collection.upsert(documents=documents, metadatas=metadatas, ids=ids)
                    total_inserted += len(documents)
                    print(f"  Upserted {len(documents)} records...")
                    documents = []
                    metadatas = []
                    ids = []

    # Final Batch
    if documents:
        collection.upsert(documents=documents, metadatas=metadatas, ids=ids)
        total_inserted += len(documents)
        print(f"  Upserted final {len(documents)} records.")

    print("--- Ingestion Complete ---")
    print(f"Total documents now in DB: {collection.count()}")

if __name__ == "__main__":
    main()