from typing import TypedDict, Any
from langgraph.graph import StateGraph, END

# Define Agent State
class CleaningState(TypedDict):
    invoice_data: dict
    logs: list
    is_valid: bool
    error: str

# Node 1: Validate Fields
def validate_fields(state: CleaningState):
    data = state["invoice_data"]
    required_fields = ["invoice_no", "total_amount", "items"]
    missing = [f for f in required_fields if f not in data or not data[f]]
    
    if missing:
        state["is_valid"] = False
        state["error"] = f"Missing fields: {missing}"
        state["logs"].append("Field validation failed.")
    else:
        state["logs"].append("Field validation passed.")
    
    return state

# Node 2: Validate Amounts
def validate_amounts(state: CleaningState):
    if not state["is_valid"]: 
        return state
        
    data = state["invoice_data"]
    try:
        # Simple check: sum of items should match total (approx)
        items_total = sum(item.get("amount", 0) for item in data.get("items", []))
        invoice_total = data.get("total_amount", 0)
        
        if abs(items_total - invoice_total) > 1.0: # Tolerance
            state["logs"].append(f"Amount mismatch warning: Items({items_total}) != Total({invoice_total})")
        else:
            state["logs"].append("Amount validation passed.")
    except Exception as e:
        state["logs"].append(f"Amount validation error: {str(e)}")
    
    return state

# Node 3: Normalize & Infer State
def normalize_data(state: CleaningState):
    if not state["is_valid"]:
        return state
    
    data = state["invoice_data"]
    # Example logic: Infer "Intra-state" if states match
    supplier_state = data.get("supplier_state", "").lower()
    buyer_state = data.get("buyer_state", "").lower()
    
    if supplier_state and buyer_state:
        data["transaction_type"] = "Intra-state" if supplier_state == buyer_state else "Inter-state"
    else:
        data["transaction_type"] = "Unknown"
        
    state["logs"].append(f"Normalized transaction type: {data['transaction_type']}")
    state["invoice_data"] = data
    return state

# Build Graph
builder = StateGraph(CleaningState)

builder.add_node("validate_fields", validate_fields)
builder.add_node("validate_amounts", validate_amounts)
builder.add_node("normalize_data", normalize_data)

builder.set_entry_point("validate_fields")

builder.add_edge("validate_fields", "validate_amounts")
builder.add_edge("validate_amounts", "normalize_data")
builder.add_edge("normalize_data", END)

cleaning_graph = builder.compile()

# Test Helper
def run_cleaning_agent(invoice_data):
    initial_state = {
        "invoice_data": invoice_data,
        "logs": [],
        "is_valid": True,
        "error": ""
    }
    result = cleaning_graph.invoke(initial_state)
    return result

if __name__ == "__main__":
    # Test
    sample_invoice = {
        "invoice_no": "INV-101",
        "total_amount": 100.0,
        "supplier_state": "Delhi",
        "buyer_state": "Delhi",
        "items": [{"amount": 50}, {"amount": 50}]
    }
    print("Cleaned Result:", run_cleaning_agent(sample_invoice))
