import requests
from sentence_transformers import SentenceTransformer

PINECONE_API_KEY = "pcsk_237Kxu_3J1tXeQQfmfVvRbSk7ynDnCHa4kMzsPfFPMVaP1cV9fvVBPNJfWBM5sL3AZeWzf"
INDEX_NAME = "gst-rules-index"

# Get host
headers = {"Api-Key": PINECONE_API_KEY}
resp = requests.get(f"https://api.pinecone.io/indexes/{INDEX_NAME}", headers=headers)
host = resp.json()['host']

print(f"Querying index at: {host}")

# Test query
model = SentenceTransformer("all-MiniLM-L6-v2")
query_text = "What is the GST rate for mobile phones?"
query_embedding = model.encode([query_text])[0].tolist()

url = f"https://{host}/query"
headers = {
    "Api-Key": PINECONE_API_KEY,
    "Content-Type": "application/json"
}
payload = {
    "vector": query_embedding,
    "topK": 3,
    "includeMetadata": True
}

resp = requests.post(url, json=payload, headers=headers)
data = resp.json()

print(f"\nQuery: {query_text}")
print(f"Matches found: {len(data.get('matches', []))}")

for i, match in enumerate(data.get('matches', [])):
    print(f"\n--- Match {i+1} (Score: {match.get('score', 0):.4f}) ---")
    print(match.get('metadata', {}).get('text', 'No text')[:200])
