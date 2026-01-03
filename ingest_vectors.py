import os
import json
import chromadb
from chromadb.utils import embedding_functions
import uuid

# --- CONFIGURATION ---
DB_PATH = "./chroma_db"
COLLECTION_NAME = "financial_knowledge"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

# Global Client (Initialize once)
client = chromadb.PersistentClient(path=DB_PATH)
ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL_NAME)
collection = client.get_or_create_collection(name=COLLECTION_NAME, embedding_function=ef)

def ingest_single_file(file_path, source_type):
    """
    Process ONE specific JSON file and add it to the DB.
    """
    print(f"⚡ Ingesting file: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            json_content = json.load(f)
    except Exception as e:
        print(f"❌ Error reading JSON: {e}")
        return

    documents = []
    metadatas = []
    ids = []
    
    items = json_content.get("data", [])
    if not isinstance(items, list):
        print(f"⚠️ Warning: 'data' is not a list in {file_path}")
        return

    filename = os.path.basename(file_path)

    for item in items:
        text_content = item.get("text", "")
        category_type = item.get("type", "UNKNOWN")

        if not text_content or len(text_content) < 5:
            continue

        documents.append(text_content)
        metadatas.append({
            "source_type": source_type,
            "filename": filename,
            "category": category_type,
            "origin_source": filename.replace(".json", "")
        })
        ids.append(f"{filename}-{uuid.uuid4()}")

    if documents:
        collection.upsert(documents=documents, metadatas=metadatas, ids=ids)
        print(f"✅ Successfully added {len(documents)} records from {filename}")
    else:
        print(f"⚠️ No valid data found in {filename}")

# Keeping the original batch logic for manual runs
def process_all_folders():
    DATA_DIRS = {
        "retail": "./data_processed/retail",
        "institutional": "./data_processed/institutional"
    }
    for source, directory in DATA_DIRS.items():
        if os.path.exists(directory):
            for f in os.listdir(directory):
                if f.endswith(".json"):
                    ingest_single_file(os.path.join(directory, f), source)

if __name__ == "__main__":
    process_all_folders()