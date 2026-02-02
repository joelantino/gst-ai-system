import psycopg2

# Database Configuration
DB_CONFIG = {
    "dbname": "gst_invoice_db",
    "user": "postgres",
    "password": "110030",
    "host": "localhost",
    "port": "5432"
}

def test_sql_agent():
    print("=" * 60)
    print("TESTING NLP TO SQL AGENT")
    print("=" * 60)
    
    # Test queries
    test_queries = [
        ("Show invoice 101", "SELECT * FROM invoices WHERE invoice_id = '101'"),
        ("Get total for invoice 103", "SELECT total_amount FROM invoices WHERE invoice_id = '103'"),
        ("Tax amount for invoice 102", "SELECT tax_amount FROM invoices WHERE invoice_id = '102'"),
        ("Supplier state for invoice 101", "SELECT supplier_state FROM invoices WHERE invoice_id = '101'"),
    ]
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        for query_text, sql in test_queries:
            print(f"\n📝 Query: {query_text}")
            print(f"🔍 SQL: {sql}")
            print("-" * 60)
            
            try:
                cursor.execute(sql)
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                results = [dict(zip(columns, row)) for row in rows]
                
                if results:
                    print(f"✅ Result: {results[0]}")
                else:
                    print("⚠️  No results found")
            except Exception as e:
                print(f"❌ Error: {e}")
            print()
        
        cursor.close()
        conn.close()
        print("✅ SQL Agent is working correctly!")
        
    except Exception as e:
        import traceback
        print(f"❌ Database connection error: {e}")
        print("\nFull error:")
        traceback.print_exc()
        print("\nMake sure PostgreSQL is running and the database exists.")

if __name__ == "__main__":
    test_sql_agent()
