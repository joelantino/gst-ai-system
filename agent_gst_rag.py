import json
import numpy as np
import os
import google.generativeai as genai
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# --- USER CONFIGURATION ---
# PASTE YOUR GEMINI API KEY HERE
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE"
# -------------------------

# Configuration
VECTOR_DB_PATH = "./gst_vector_store.json"
MODEL_NAME = "all-MiniLM-L6-v2"

class GSTRagAgent:
    def __init__(self):
        if not os.path.exists(VECTOR_DB_PATH):
            raise FileNotFoundError(f"Vector DB not found at {VECTOR_DB_PATH}. Run setup_vector_db.py first.")
            
        print("Loading Vector Store...")
        with open(VECTOR_DB_PATH, "r") as f:
            data = json.load(f)
            
        self.chunks = data["chunks"]
        self.embeddings = np.array(data["embeddings"])
        
        print("Loading Embedding Model...")
        self.model = SentenceTransformer(MODEL_NAME)
        
        # Configure Gemini
        self.llm_model = None
        if GEMINI_API_KEY and len(GEMINI_API_KEY) > 20:
            genai.configure(api_key=GEMINI_API_KEY)
            self.llm_available = True
            
            # Dynamic Model Selection
            print("Searching for available Gemini models...")
            try:
                found_model = None
                # Prioritize flash models for speed
                preferred_order = ["flash", "pro", "1.5", "1.0"] 
                
                all_models = [m for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                
                # Sort models based on preference
                all_models.sort(key=lambda x: any(p in x.name for p in preferred_order), reverse=True)

                for m in all_models:
                    try:
                        test_model = genai.GenerativeModel(m.name)
                        test_model.generate_content("Hi")
                        self.llm_model = test_model
                        print(f"✅ Connected to LLM: {m.name}")
                        found_model = m.name
                        break
                    except:
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
        # 1. Embed Query
        query_embedding = self.model.encode([query])
        
        # 2. Calculate Similarity (Cosine)
        similarities = cosine_similarity(query_embedding, self.embeddings)[0]
        
        # 3. Get Top K indices
        top_indices = similarities.argsort()[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            results.append(self.chunks[idx])
            
        return results

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
