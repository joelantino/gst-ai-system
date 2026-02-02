# AEGIS GST System - Phases 3 to 7 Implementation

This directory contains the implementation of the advanced AI phases for the GST Intelligence System.

## Prerequisites
Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Phase 3: GST Rules Vector Store (Native)
- **File**: `gst_rules.txt` contains the raw knowledge base.
- **File**: `setup_vector_db.py` creates the embeddings.
- **Tech**: Uses `sentence-transformers` + `numpy` (Cosine Similarity) instead of ChromaDB for lightweight, dependency-free execution on all environments.
- **Action**: Run the setup script once to initialize the store:
  ```bash
  python setup_vector_db.py
  ```

## Phase 4: GST RAG Agent (Agent 2)
- **File**: `agent_gst_rag.py`
- **Functionality**: Connects to the Vector DB and retrieves rules to answer GST questions.
- **Usage**:
  ```python
  from agent_gst_rag import GSTRagAgent
  agent = GSTRagAgent()
  print(agent.generate_answer("What is the tax rate for services?"))
  ```

## Phase 5: LangGraph Cleaning Agent
- **File**: `agent_cleaning_langgraph.py`
- **Functionality**: Validates and normalizes invoice data using a directed graph.
- **Usage**:
  ```python
  from agent_cleaning_langgraph import run_cleaning_agent
  cleaned_data = run_cleaning_agent(raw_invoice_dict)
  ```

## Phase 6 & 7: Orchestrator & End-to-End
- **File**: `agent_orchestrator.py`
- **Functionality**: Main entry point. Classifies user queries (`SQL`, `RAG`, `CALCULATION`) and routes them to the appropriate agent.
- **Action**: Run the orchestrator to test the full system:
  ```bash
  python agent_orchestrator.py
  ```

## Notes
- Ensure PostgreSQL is running for `agent_invoice_sql.py` features.
- The RAG agent currently simulates the final LLM generation step to save API costs/setup time. Integrate your `Gemini` or `OpenAI` key in `agent_gst_rag.py` for full text generation.
