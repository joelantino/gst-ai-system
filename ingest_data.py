import pandas as pd
import psycopg2
import os
import glob
from psycopg2.extras import execute_values

# DB Configuration (Matches agent_invoice_sql.py)
DB_CONFIG = {
    "dbname": "gst_invoice_db",
    "user": "postgres",
    "password": "110030",
    "host": "localhost",
    "port": "5432"
}

DATA_DIR = "./dataset"

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

def ingest_data():
    # 1. Find CSV File
    csv_files = glob.glob(os.path.join(DATA_DIR, "*.csv"))
    if not csv_files:
        print(f"No CSV file found in {DATA_DIR}. Please place your dataset file there.")
        return

    file_path = csv_files[0]
    print(f"Processing file: {file_path}")

    # 2. Read Data
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    # 3. Basic Cleaning (Mapping common column names to our Schema)
    # Expected Schema: invoice_id, date, total_amount, tax_amount, supplier_state, buyer_state
    
    # Normalize column names to lowercase
    df.columns = [c.lower().strip() for c in df.columns]
    
    # Heuristic mapping (Adjust these based on your actual CSV columns)
    # If your CSV has different names, the script might need adjustment.
    
    # Ensure ID exists (generate if missing)
    if 'invoice_id' not in df.columns:
        if 'invoice no' in df.columns:
            df.rename(columns={'invoice no': 'invoice_id'}, inplace=True)
        else:
            print("Warning: No 'invoice_id' column. generating sequential IDs.")
            df['invoice_id'] = range(1001, 1001 + len(df))

    # Ensure Amounts
    if 'total_amount' not in df.columns and 'total' in df.columns:
        df.rename(columns={'total': 'total_amount'}, inplace=True)
    
    if 'tax_amount' not in df.columns and 'tax' in df.columns:
        df.rename(columns={'tax': 'tax_amount'}, inplace=True)

    # Ensure States (Defaulting if missing for demo)
    if 'supplier_state' not in df.columns:
        df['supplier_state'] = 'Delhi' # Default
    if 'buyer_state' not in df.columns:
        df['buyer_state'] = 'Delhi' # Default
        
    # Fill NaNs
    df.fillna(0, inplace=True)

    # 4. Insert into DB
    conn = get_db_connection()
    cursor = conn.cursor()

    print(f"Inserting {len(df)} records into 'invoices' table...")

    insert_query = """
    INSERT INTO invoices (invoice_id, total_amount, tax_amount, supplier_state, buyer_state)
    VALUES %s
    ON CONFLICT (invoice_id) DO NOTHING;
    """

    # Prepare data list
    data_to_insert = [
        (
            str(row['invoice_id']), 
            float(row.get('total_amount', 0)), 
            float(row.get('tax_amount', 0)), 
            row.get('supplier_state', ''), 
            row.get('buyer_state', '')
        )
        for index, row in df.iterrows()
    ]

    try:
        execute_values(cursor, insert_query, data_to_insert)
        conn.commit()
        print("Data ingestion complete!")
    except Exception as e:
        print(f"Database Error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    ingest_data()
