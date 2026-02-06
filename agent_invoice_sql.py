import psycopg2
import re

# -------- Step 2.2: Intent Classification --------
def classify_intent(query: str) -> str:
    q = query.lower()

    if "interstate" in q:
        return "GET_INTERSTATE_INVOICES"

    if "total" in q and "invoice" in q:
        return "GET_TOTAL_AMOUNT"

    if "tax" in q or "gst" in q:
        return "GET_TAX_AMOUNT"

    if "invoice" in q:
        return "GET_INVOICE_BY_ID"

    return "UNKNOWN"


# -------- Step 2.3: SQL Templates --------
SQL_TEMPLATES = {
    "GET_INVOICE_BY_ID":
        "SELECT * FROM invoices WHERE invoice_id = %s",

    "GET_TOTAL_AMOUNT":
        "SELECT total_amount FROM invoices WHERE invoice_id = %s",

    "GET_TAX_AMOUNT":
        "SELECT tax_amount FROM invoices WHERE invoice_id = %s",

    "GET_INTERSTATE_INVOICES":
        "SELECT * FROM invoices WHERE supplier_state != buyer_state",

    "GET_ALL_INVOICES":
        "SELECT * FROM invoices"
}


import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# -------- Helpers --------
def extract_invoice_id(query: str):
    match = re.search(r"\b(\d+)\b", query)
    return int(match.group(1)) if match else None


def get_db_connection():
    return psycopg2.connect(
        dbname="gst_invoice_db",
        user="postgres",
        password=os.getenv("DB_PASSWORD"),
        host="localhost",
        port="5432"
    )


# -------- Step 2.4: Execution Layer --------
def run_query(user_query: str):
    intent = classify_intent(user_query)
    sql = SQL_TEMPLATES.get(intent)

    if not sql:
        return {"error": "Unsupported query intent"}

    invoice_id = extract_invoice_id(user_query)

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        if "%s" in sql:
            if not invoice_id:
                return {"error": "Invoice ID not found in query"}
            cursor.execute(sql, (invoice_id,))
        else:
            cursor.execute(sql)

        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]

        return [dict(zip(columns, row)) for row in rows]

    finally:
        cursor.close()
        conn.close()
