import json
import numpy as np
import os
from sentence_transformers import SentenceTransformer

# Configuration
VECTOR_DB_PATH = "./gst_vector_store.json"
SOURCE_FILE = "gst_rules.txt"
MODEL_NAME = "all-MiniLM-L6-v2"

def setup_database():
    print(f"Initializing Native Vector Store...")
    
    # 1. Load Data
    if not os.path.exists(SOURCE_FILE):
        print(f"Error: {SOURCE_FILE} not found.")
        return

    with open(SOURCE_FILE, "r") as f:
        content = f.read()

    # Simple chunking by double newline (sections)
    chunks = [chunk.strip() for chunk in content.split("\n\n") if chunk.strip()]
    print(f"Found {len(chunks)} rule chunks.")

    # 2. Generate Embeddings using SentenceTransformer
    print("Loading embedding model (this may take a moment)...")
    model = SentenceTransformer(MODEL_NAME)
    extract_embeddings = model.encode(chunks)

    # 3. Store Data (Simulating a Vector DB with JSON/Numpy)
    # converting numpy array to list for JSON serialization
    vector_store = {
        "chunks": chunks,
        "embeddings": extract_embeddings.tolist() 
    }

    with open(VECTOR_DB_PATH, "w") as f:
        json.dump(vector_store, f)

    print(f"Successfully saved {len(chunks)} rules and embeddings to {VECTOR_DB_PATH}.")

if __name__ == "__main__":
    setup_database()
