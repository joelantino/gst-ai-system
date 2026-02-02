# 🧠 GST Intelligence System

A multi-agent AI system for intelligent GST (Goods and Services Tax) query processing, combining SQL database lookups, RAG-based legal reasoning, and automated tax calculations.

## 🌟 Features

### Phase 1-2: Invoice Database & SQL Agent
- PostgreSQL database for invoice storage
- Intent-based query classification
- Safe SQL template execution
- Support for invoice lookups, tax amounts, and interstate detection

### Phase 3-4: GST Rules Vector Store & RAG Agent
- Semantic search over GST legal rules
- Native vector store (no heavy dependencies)
- Retrieval-Augmented Generation for accurate answers
- Grounded responses (no hallucinations)

### Phase 5: LangGraph Cleaning Agent
- Automated invoice data validation
- Field presence checks
- Amount consistency verification
- State inference (Inter-state vs Intra-state)

### Phase 6-7: Orchestrator & End-to-End Intelligence
- Smart query routing (SQL, RAG, or Calculation)
- Hybrid reasoning (fetch data + apply rules)
- IGST vs CGST/SGST breakdown
- Interactive CLI interface

## 📋 Prerequisites

- Python 3.9+
- PostgreSQL 12+
- Google Gemini API Key (optional, for LLM generation)

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup PostgreSQL Database
Create database and tables:
```sql
CREATE DATABASE gst_invoice_db;

CREATE TABLE invoices (
    invoice_id VARCHAR(50) PRIMARY KEY,
    total_amount DECIMAL(10, 2),
    tax_amount DECIMAL(10, 2),
    supplier_state VARCHAR(100),
    buyer_state VARCHAR(100)
);
```

Update connection details in `agent_invoice_sql.py` (lines 49-54).

### 3. Initialize Vector Store
```bash
python setup_vector_db.py
```

### 4. Load Sample Data (Optional)
```bash
python ingest_data.py
```

### 5. Configure API Key (Optional)
Edit `agent_gst_rag.py` and add your Gemini API key:
```python
GEMINI_API_KEY = "YOUR_KEY_HERE"
```

### 6. Run the System
```bash
python agent_orchestrator.py
```

## 💡 Usage Examples

### Ask about GST Rules
```
>> User: What is the GST rate for mobile phones?
>> Agent: Mobile phones fall under the 12% GST slab...
```

### Query Invoice Data
```
>> User: Get total amount for invoice 101
>> Agent: [{'total_amount': 1180.00}]
```

### Calculate Tax
```
>> User: Calculate 18% GST on invoice 103
>> Agent: {
    "action": "Calculated GST for Invoice",
    "invoice_id": 103,
    "calculation": {
        "taxable_value": 23600.00,
        "rate": 18,
        "tax_amount": 4248.00,
        ...
    }
}
```

## 📂 Project Structure

```
gst-ai-system/
├── agent_invoice_sql.py       # Phase 2: SQL Agent
├── agent_gst_rag.py           # Phase 4: RAG Agent
├── agent_cleaning_langgraph.py # Phase 5: Cleaning Agent
├── agent_orchestrator.py       # Phase 6-7: Main Orchestrator
├── setup_vector_db.py         # Vector store initialization
├── ingest_data.py             # Database ingestion script
├── gst_rules.txt              # GST knowledge base
├── requirements.txt           # Python dependencies
├── dataset/                   # Invoice data folder
│   └── sample_invoices.csv
└── README.md
```

## 🧪 Testing Individual Agents

### Test RAG Agent
```bash
python agent_gst_rag.py
```

### Test Cleaning Agent
```bash
python agent_cleaning_langgraph.py
```

### Check Database Connection
```bash
python check_db_status.py
```

## 🔧 Configuration

### Database Connection
Edit `agent_invoice_sql.py`:
```python
DB_CONFIG = {
    "dbname": "gst_invoice_db",
    "user": "postgres",
    "password": "YOUR_PASSWORD",
    "host": "localhost",
    "port": "5432"
}
```

### Add More GST Rules
1. Edit `gst_rules.txt`
2. Rerun `python setup_vector_db.py`

## 🏗️ Architecture

```
User Query
    ↓
Orchestrator (Query Classification)
    ↓
    ├── SQL Agent → PostgreSQL
    ├── RAG Agent → Vector Store → LLM
    └── Calculator → SQL + Math Engine
```

## 📊 Supported Query Types

| Type | Example | Agent |
|------|---------|-------|
| General GST | "What is IGST?" | RAG |
| Invoice Lookup | "Show invoice 101" | SQL |
| Tax Calculation | "Calculate 12% on invoice 102" | Hybrid |

## 🛡️ Security Notes

- Never commit API keys to Git
- Use environment variables for sensitive data
- SQL templates prevent injection attacks

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push and create a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 👨‍💻 Author

Created as part of GST Training System (2026)

## 🙏 Acknowledgments

- LangGraph for agent orchestration
- Sentence-Transformers for embeddings
- Google Gemini for LLM capabilities
