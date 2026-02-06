import json
import numpy as np
import os
import requests
import google.generativeai as genai
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- USER CONFIGURATION ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PINECONE_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("INDEX_NAME", "gst-rules-index")
# -------------------------

MODEL_NAME = "all-MiniLM-L6-v2"

class GSTRagAgent:
    def __init__(self):
        print("Initializing RAG Agent (Pinecone REST)...")
        self.model = SentenceTransformer(MODEL_NAME)
        
        # Get Pinecone Host
        self.pinecone_host = None
        try:
            headers = {"Api-Key": PINECONE_KEY}
            resp = requests.get(f"https://api.pinecone.io/indexes/{INDEX_NAME}", headers=headers)
            if resp.status_code == 200:
                self.pinecone_host = resp.json()['host']
                print(f"✅ Connected to Pinecone Index: {self.pinecone_host}")
            else:
                print(f"❌ Failed to find Pinecone Index '{INDEX_NAME}'. Run setup first.")
        except Exception as e:
            print(f"Error connecting to Pinecone: {e}")

        # Configure Gemini
        self.llm_model = None
        if GEMINI_API_KEY and len(GEMINI_API_KEY) > 20:
            genai.configure(api_key=GEMINI_API_KEY)
            self.llm_available = True
            
            # Dynamic Model Selection
            print("Searching for available Gemini models...")
            try:
                found_model = None
                
                all_models = [m for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                
                # Filter out image generation models
                text_models = [m for m in all_models if 'image' not in m.name.lower()]
                
                # Prioritize flash models for speed, then pro
                text_models.sort(key=lambda x: (
                    'flash' in x.name.lower(),
                    '2.0' in x.name or '2.5' in x.name,
                    'pro' in x.name.lower()
                ), reverse=True)

                for m in text_models:
                    try:
                        print(f"Testing: {m.name}")
                        test_model = genai.GenerativeModel(m.name)
                        test_model.generate_content("Hi")
                        self.llm_model = test_model
                        print(f"✅ Connected to LLM: {m.name}")
                        found_model = m.name
                        break
                    except Exception as e:
                        print(f"   ❌ Failed: {str(e)[:50]}")
                        continue
                
                if not found_model:
                     print("❌ Warning: No working model found in your account quota.")
                     self.llm_available = False
                     
            except Exception as e:
                print(f"Error listing models: {e}")
                self.llm_available = False
        else:
            self.llm_available = False
            print("Warning: No API Key set. Using simulated responses.")

    def retrieve_rules(self, query, top_k=2):
        if not self.pinecone_host:
            return ["Error: Pinecone not connected."]

        # 1. Embed Query
        query_embedding = self.model.encode([query])[0].tolist()
        
        # 2. Query Pinecone REST
        url = f"https://{self.pinecone_host}/query"
        headers = {
            "Api-Key": PINECONE_KEY,
            "Content-Type": "application/json"
        }
        payload = {
            "vector": query_embedding,
            "topK": top_k,
            "includeMetadata": True
        }
        
        try:
            resp = requests.post(url, json=payload, headers=headers)
            data = resp.json()
            matches = data.get('matches', [])
            
            results = [m['metadata']['text'] for m in matches if 'metadata' in m]
            return results
        except Exception as e:
            return [f"Error querying Pinecone: {e}"]

    def format_with_llm(self, query, raw_data):
        """Uses LLM to format raw data results into structured sentences."""
        if not self.llm_available:
            return f"Raw Data: {raw_data}"
            
        prompt = f"""
        You are a GST Assistant. Convert the following RAW DATA into a professionally structured natural language sentence or paragraph.
        The user asked: "{query}"
        
        RAW DATA FROM DATABASE/CALCULATOR:
        {json.dumps(raw_data, indent=2, default=str)}
        
        INSTRUCTIONS:
        1. Be polite and professional.
        2. Use the data provided to answer the user's question directly.
        3. Do not invent facts not present in the raw data.
        4. If the data is an empty list, say the information was not found.
        
        FINAL SENTENCE:
        """
        
        try:
            response_obj = self.llm_model.generate_content(prompt)
            return response_obj.text.strip()
        except Exception as e:
            return f"Error formatting response: {e}. Raw Data: {raw_data}"

    def generate_answer(self, query):
        # 1. Retrieve
        rules = self.retrieve_rules(query)
        context = "\n\n".join(rules)

        # 2. Augment Prompt
        # Prompt Engineering for Legal/Fact-based answer
        prompt = f"""
        You are an expert GST Assistant. Answer the question based STRICTLY on the provided rules.
        Do not use external knowledge. If the answer is not in the rules, state that you don't know.
        
        CONTEXT RULES:
        {context}

        QUESTION:
        {query}
        
        ANSWER (Be concise and cite the specific rule/rate):
        """

        # 3. Generate
        if self.llm_available:
            try:
                response_obj = self.llm_model.generate_content(prompt)
                response = response_obj.text
            except Exception as e:
                response = f"Error generating content: {e}"
        else:
            # Fallback Mock
            response = f"[Simulated LLM (No API Key)]: Based on the rules retrieved (e.g., '{rules[0][:30]}...'), here is the answer: [Please add API Key to see real answer]"
        
        return {
            "query": query,
            "retrieved_context": rules,
            "generated_answer": response
        }

if __name__ == "__main__":
    agent = GSTRagAgent()
    print("\n--- TEST ANSWER ---")
    print(agent.generate_answer("How much tax on mobile phones?"))
