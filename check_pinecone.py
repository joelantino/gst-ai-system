import requests

PINECONE_API_KEY = "pcsk_237Kxu_3J1tXeQQfmfVvRbSk7ynDnCHa4kMzsPfFPMVaP1cV9fvVBPNJfWBM5sL3AZeWzf"

headers = {
    "Api-Key": PINECONE_API_KEY,
    "Content-Type": "application/json"
}

print("Checking Pinecone account...")
resp = requests.get("https://api.pinecone.io/indexes", headers=headers)

if resp.status_code == 200:
    data = resp.json()
    indexes = data.get('indexes', [])
    
    if len(indexes) == 0:
        print("❌ No indexes found in your Pinecone account.")
    else:
        print(f"✅ Found {len(indexes)} index(es):")
        for idx in indexes:
            print(f"\n  Name: {idx['name']}")
            print(f"  Host: {idx.get('host', 'N/A')}")
            print(f"  Status: {idx.get('status', {}).get('state', 'Unknown')}")
            print(f"  Dimension: {idx.get('dimension', 'N/A')}")
else:
    print(f"❌ Error: {resp.status_code}")
    print(resp.text)
