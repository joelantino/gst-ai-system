import os
import time
import requests
import json
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- USER CONFIGURATION ---
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("INDEX_NAME", "gst-rules-index")
# -------------------------

MODEL_NAME = "all-MiniLM-L6-v2"
SOURCE_FILE = "gst_rules.txt"

def setup_database():
    headers = {
        "Api-Key": PINECONE_API_KEY,
        "Content-Type": "application/json"
    }

    print("Checking Pinecone Index via REST API...")
    
    # 1. List Indexes
    resp = requests.get("https://api.pinecone.io/indexes", headers=headers)
    if resp.status_code != 200:
        print(f"❌ Error listing indexes: {resp.text}")
        return
    
    indexes_data = resp.json().get('indexes', [])
    existing_names = [idx['name'] for idx in indexes_data]
    print(f"Existing Indexes: {existing_names}")

    host = None

    if INDEX_NAME not in existing_names:
        print(f"Creating new Serverless index: {INDEX_NAME}...")
        create_payload = {
            "name": INDEX_NAME,
            "dimension": 384,
            "metric": "cosine",
            "spec": {
                "serverless": {
                    "cloud": "aws",
                    "region": "us-east-1"
                }
            }
        }
        resp = requests.post("https://api.pinecone.io/indexes", json=create_payload, headers=headers)
        if resp.status_code != 201:
             print(f"❌ Failed to create index: {resp.text}")
             return
        print("Index creating... waiting 30s...")
        time.sleep(30)
    else:
        print(f"Index '{INDEX_NAME}' already exists.")

    # 2. Get Index Host
    resp = requests.get(f"https://api.pinecone.io/indexes/{INDEX_NAME}", headers=headers)
    if resp.status_code != 200:
        print(f"❌ Failed to get index details: {resp.text}")
        return
    
    host = resp.json()['host']
    print(f"✅ Target Host: {host}")

    # 3. Embed Data
    print("Loading Rule Data...")
    if not os.path.exists(SOURCE_FILE):
        print(f"Error: {SOURCE_FILE} not found.")
        return

    with open(SOURCE_FILE, "r") as f:
        content = f.read()

    chunks = [chunk.strip() for chunk in content.split("\n\n") if chunk.strip()]
    print(f"Found {len(chunks)} rule chunks to upsert.")

    print("Generating Embeddings...")
    model = SentenceTransformer(MODEL_NAME)
    embeddings = model.encode(chunks)

    # 4. Upsert
    vectors = []
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        vectors.append({
            "id": f"rule_{i}",
            "values": embedding.tolist(),
            "metadata": {"text": chunk}
        })
    
    upsert_url = f"https://{host}/vectors/upsert"
    
    # Batch upsert logic (Pinecone supports max 2MB request, strict batching is safe)
    batch_size = 50
    for i in range(0, len(vectors), batch_size):
        batch = vectors[i:i+batch_size]
        payload = {"vectors": batch}
        print(f"Upserting batch {i} to {i+len(batch)}...")
        resp = requests.post(upsert_url, json=payload, headers=headers)
        if resp.status_code != 200:
            print(f"❌ Upsert failed: {resp.text}")
        else:
            print(f"Batch {i} success: {resp.json()}")

    print("✅ Full Knowledge Base uploaded to Pinecone!")

if __name__ == "__main__":
    setup_database()
