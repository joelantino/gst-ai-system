try:
    print("Testing imports...")
    from pinecone import Pinecone, ServerlessSpec
    print("Imports successful!")
except Exception as e:
    print(f"Import Error: {e}")

try:
    print("Testing client init...")
    # Using your key directly for test
    pc = Pinecone(api_key="pcsk_237Kxu_3J1tXeQQfmfVvRbSk7ynDnCHa4kMzsPfFPMVaP1cV9fvVBPNJfWBM5sL3AZeWzf")
    print("Client init success")
    print(pc.list_indexes())
except Exception as e:
    print(f"Client init error: {e}")
