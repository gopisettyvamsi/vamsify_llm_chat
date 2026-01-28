
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv(r'C:\Users\VamsiGopisetty\.gemini\antigravity\scratch\offline-llm-chat\backend\.env')

try:
    conn = mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', 'root'),
        database=os.getenv('DB_NAME', 'vamsify_llm_chat')
    )
    cursor = conn.cursor()
    cursor.execute("DESCRIBE conversations")
    columns = [row[0] for row in cursor.fetchall()]
    print("Columns in conversations:", columns)
    
    if 'history' in columns:
        print("SUCCESS: history column exists")
    else:
        print("FAILURE: history column MISSING")
        
except Exception as e:
    print(f"Error: {e}")
