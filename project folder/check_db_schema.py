import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

# Guessing DB name from previous `list_dir` or env. 
# app/core/config.py likely reads DATABASE_URL.
# Assuming standard `sqlite+aiosqlite:///./doxa_support.db` -> `doxa_support.db`
DB_FILE = "doxa_support_v1.db"

def check_schema():
    if not os.path.exists(DB_FILE):
        print(f"Database file {DB_FILE} not found.")
        return

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        cursor.execute("PRAGMA table_info(tickets);")
        columns = cursor.fetchall()
        print("Columns in 'tickets' table:")
        found_category = False
        found_ai_conf = False
        found_category = False
        found_ai_conf = False
        for col in columns:
            cid, name, type, notnull, dflt_value, pk = col
            if name == "category":
                found_category = True
            if name == "ai_confidence_score":
                found_ai_conf = True
        
        if found_category and found_ai_conf:
            print("SCHEMA_OK: All columns present.")
        else:
            print(f"SCHEMA_ERROR: Category={found_category}, AI_Conf={found_ai_conf}")
            
    except Exception as e:
        print(f"Error inspecting DB: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_schema()
