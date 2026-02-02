import re
import agent_invoice_sql
from agent_gst_rag import GSTRagAgent

class OrchestratorAgent:
    def __init__(self):
        self.rag_agent = GSTRagAgent()

    def classify_query(self, query):
        q = query.lower()
        
        # Calculation implied
        if "calculate" in q:
            return "CALCULATION"

        # SQL Intent: Specific invoice data
        if "invoice" in q and any(char.isdigit() for char in q):
            # Likely asking about a specific invoice ID or sum of invoices
            return "SQL_AGENT"
        
        # RAG Intent: General knowledge
        if "rate" in q or "slab" in q or "rule" in q or "what is" in q:
            return "RAG_AGENT"
        
        # Calculation implied
        if "calculate" in q:
            return "CALCULATION"
            
        # Default fallback
        return "RAG_AGENT"

    def calculate_gst(self, amount, rate, is_interstate):
        tax = amount * (rate / 100)
        return {
            "taxable_value": amount,
            "rate": rate,
            "tax_amount": tax,
            "total_payable": amount + tax,
            "breakdown": {
                "IGST": tax if is_interstate else 0,
                "CGST": tax/2 if not is_interstate else 0,
                "SGST": tax/2 if not is_interstate else 0
            }
        }

    def run(self, user_query):
        intent = self.classify_query(user_query)
        print(f"--- Orchestrator: Classified as {intent} ---")
        
        if intent == "SQL_AGENT":
            return agent_invoice_sql.run_query(user_query)
        
        elif intent == "RAG_AGENT":
            return self.rag_agent.generate_answer(user_query)
            
        elif intent == "CALCULATION":
            # Example Hybrid Logic: "Calculate 18% GST on Invoice #101"
            # 1. Extract Invoice number -> SQL
            inv_id = agent_invoice_sql.extract_invoice_id(user_query)
            if not inv_id:
                return "Could not identify invoice ID for calculation."
            
            # Get Invoice Total
            sql_result = agent_invoice_sql.run_query(f"total amount invoice {inv_id}")
            # sql_result expected list of dicts, e.g. [{'total_amount': 5000}]
            
            if not sql_result or 'error' in sql_result:
                return f"Invoice {inv_id} not found."
                
            amount = float(sql_result[0].get('total_amount', 0))
            
            # 2. Extract Rate likely from query
            rate_match = re.search(r"(\d+)%", user_query)
            rate = float(rate_match.group(1)) if rate_match else 18.0 # Default fallback
            
            # 3. Determine State (Mocking Inter-state check or fetching from DB if extended)
            # For now, let's assume intra-state default or random
            is_interstate = False 
            
            result = self.calculate_gst(amount, rate, is_interstate)
            return {
                "action": "Calculated GST for Invoice",
                "invoice_id": inv_id,
                "calculation": result
            }
            
        return "Query not understood."

if __name__ == "__main__":
    system = OrchestratorAgent()
    
    print("\n--- GST INTELLIGENCE SYSTEM ---")
    print("Ask about GST rules, Invoice data, or Calculations.")
    print("Type 'exit' to quit.\n")
    
    while True:
        try:
            user_input = input(">> User: ")
            if user_input.lower() in ["exit", "quit"]:
                break
                
            response = system.run(user_input)
            print(f">> Agent: {response}\n")
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")
